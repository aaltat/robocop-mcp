# Copyright (c) 2025 Tatu Aalto
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software
# and associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute,
# sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
# BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import logging
import os
from dataclasses import dataclass
from pathlib import Path

import tomli  # tomli is for Python versions < 3.11 move to tomllib when 3.11+ is minimum
from mcp.server.fastmcp import FastMCP
from robocop import config as robocop_config  # type: ignore
from robocop.linter.diagnostics import Diagnostic  # type: ignore
from robocop.linter.rules import RuleFilter, filter_rules_by_category  # type: ignore
from robocop.linter.runner import RobocopLinter  # type: ignore
from robocop.run import check_files  # type: ignore

mcp = FastMCP("op-robocop-mcp")
logging.basicConfig(format="%(asctime)s %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p", level=logging.INFO)
logger = logging.getLogger("robocop-mcp")


@dataclass
class Violation:
    file: Path
    start_line: int
    end_line: int
    start_column: int
    end_column: int
    severity: str
    rule_id: str
    description: str


@dataclass
class Rule:
    rule_id: str
    instruction: str


@dataclass
class Config:
    robocopmcp_config_file: Path | None
    rules: list[Rule]
    violation_count: int
    rule_priority: list[str]
    rule_ignore: list[str]
    robocop_configured: bool = False


def get_robocop_rules() -> list[Rule]:
    linter_config = robocop_config.LinterConfig(  # set to None to not override
        configure=None,
        select=None,
        ignore=None,
        issue_format=None,
        threshold=None,
        custom_rules=None,
        reports=None,
        persistent=None,
        compare=None,
        exit_zero=None,
    )
    overwrite_config = robocop_config.Config(
        linter=linter_config,
        formatter=None,
        file_filters=None,
        language=None,
        verbose=None,
        target_version=None,
    )
    config_manager = robocop_config.ConfigManager(overwrite_config=overwrite_config)
    runner = RobocopLinter(config_manager)
    default_config = runner.config_manager.default_config
    rules = filter_rules_by_category(
        default_config.linter.rules,  # type: ignore
        RuleFilter.ALL,
        default_config.linter.target_version,  # type: ignore
    )
    return [Rule(rule.rule_id, rule.docs) for rule in rules]


ROBOCOP_RULES = get_robocop_rules()


def _is_robocop_rule(robocop_rules: list[Rule], rule: str) -> bool:
    return any(robocop_rule.rule_id.lower() == rule.lower() for robocop_rule in robocop_rules)


def _rule_is_set(rule: Rule, current_rules: list[Rule]) -> bool:
    return any(rule.rule_id == current_rule.rule_id for current_rule in current_rules)


def _get_rule_fixes(robocop_rule: list[Rule], config: dict) -> list[Rule]:
    rules: list[Rule] = []
    if not config:
        return rules
    for key, value in config.items():
        if _is_robocop_rule(robocop_rule, key):
            rules.append(Rule(key, value))
    return rules


def _append_robocop_rules(rules: list[Rule], robocop_rules: list[Rule]) -> list[Rule]:
    all_rules: list[Rule] = []
    for rule in rules + robocop_rules:
        if _rule_is_set(rule, all_rules):
            continue
        all_rules.append(rule)
    return all_rules


def _get_violation_count(config: dict, pyproject_toml: Path) -> int:
    count = config.get("violation_count", 20)
    if isinstance(count, str):
        logger.info("violation_count in %s is string, converting to int", pyproject_toml)
        try:
            count = int(count)
        except ValueError:
            logger.warning(
                "Invalid violation_count value '%s' in %s, using default 20",
                count,
                pyproject_toml,
            )
            count = 20
    return count


def _get_rule_priority(config: dict, pyproject_toml: Path) -> list[str]:
    rule_priority = config.get("rule_priority", [])
    if isinstance(rule_priority, str):
        logger.info("rule_priority in %s is string, converting to list", pyproject_toml)
        rule_priority = [rule_priority]
    return rule_priority


def _robocop_configured_in_toml(data: dict, pyproject_toml: Path) -> bool:
    if "tool" in data and "robocop" in data["tool"]:
        logger.info("RoboCop configuration found in %s", pyproject_toml)
        robocop_configured = True
    else:
        logger.info("No RoboCop configuration found in %s", pyproject_toml)
        robocop_configured = False
    return robocop_configured


def _get_config() -> Config:
    pyproject_toml_env = os.environ.get("ROBOCOPMCP_CONFIG_FILE")
    pyproject_toml = Path(pyproject_toml_env).resolve() if pyproject_toml_env else None
    if pyproject_toml and pyproject_toml.is_file():
        with pyproject_toml.open("r+b") as file:
            data = tomli.load(file)
        robocop_mcp = data["tool"].get("robocop_mcp", {})
        rules = _get_rule_fixes(ROBOCOP_RULES, robocop_mcp)
        rules = _append_robocop_rules(rules, ROBOCOP_RULES)
        count = _get_violation_count(robocop_mcp, pyproject_toml)
        rule_priority = _get_rule_priority(robocop_mcp, pyproject_toml)
        robocop_configured = _robocop_configured_in_toml(data, pyproject_toml)
        ignore = robocop_mcp.get("ignore", [])
    else:
        logger.info("No pyproject.toml file found, using default configuration.")
        rules = ROBOCOP_RULES
        count = 20
        rule_priority = []
        robocop_configured = False
        ignore = []
    return Config(pyproject_toml, rules, count, rule_priority, ignore, robocop_configured)


def _convert_to_violations(result: list[Diagnostic]) -> list[Violation]:
    logger.info("Convert to violations")
    return [
        Violation(
            file=Path(item.source),
            start_line=item.range.start.line,
            end_line=item.range.end.line,
            start_column=item.range.start.character,
            end_column=item.range.end.character,
            severity=item.severity.name,
            rule_id=item.rule.rule_id,
            description=item.message,
        )
        for item in result
    ]


async def _run_robocop(path: str) -> list[Violation]:
    sources = [Path(path)]
    kwargs = {"sources": sources, "return_result": True, "silent": True}
    config = _get_config()
    if config.robocop_configured:
        kwargs["configuration_file"] = config.robocopmcp_config_file
    result = check_files(**kwargs)
    if result is None:
        return []
    return _convert_to_violations(result)


def _resolve_path(path: str | None) -> str:
    if path is None:
        return str(Path())
    return str(Path(path))


def _get_first_violation(violations: list[Violation], config: Config) -> Violation | None:
    for violation in violations:
        if violation.rule_id in config.rule_priority:
            return violation
    logger.info("No prioritized rule violation found.")
    for violation in violations:
        if violation.rule_id not in config.rule_ignore:
            return violation
    logger.info("No rule priority or ignore violations found, return first violation.")
    if violations:
        return violations[0]
    return None


def _filter_violations(violations: list[Violation]) -> list[Violation]:
    config = _get_config()
    filtered_violations: list[Violation] = []
    first_violation = _get_first_violation(violations, config)
    if first_violation is None:
        logger.info("No violations found to filter.")
        return filtered_violations
    for violation in violations:
        if len(filtered_violations) >= config.violation_count:
            break
        if violation.rule_id == first_violation.rule_id:
            filtered_violations.append(violation)
    return filtered_violations


def _format_report(violation: Violation) -> list[str]:
    heading = (
        f"## Violation for file {violation.file.name} in line {violation.start_line} rule {violation.rule_id}"
    )
    return [
        heading,
        "",
        f"description: {violation.description}",
        f"start line: {violation.start_column}",
        f"end line: {violation.end_column}",
        f"start column: {violation.start_column}",
        f"end column: {violation.end_column}",
        f"file: {violation.file}",
        f"rule id: {violation.rule_id}",
        f"severity: {violation.severity}",
    ]


def _is_file(path: str) -> bool:
    try:
        return Path(path).is_file()
    except OSError:
        return False


def _get_violation_fix(violation: Violation, config: Config) -> str:
    for rule in config.rules:
        if rule.rule_id == violation.rule_id:
            rule_instruction = rule.instruction
            if rule_instruction and _is_file(rule_instruction):
                with Path(rule_instruction).open("r") as file:
                    return file.read()
            return rule_instruction
    return "No solution proposed fix found"


@mcp.tool()
async def get_robocop_report(path: str | None) -> str:
    """
    Run RoboCop on the provided source code and return the report.

    Args:
        path (str | None): The path to folder or a file to analyze. If None, uses the
        current directory for analysis.

    Returns:
        str: The Robocop report in markdown format.

    Example if there is one Violation in path, which looks like this:
    Violation(
        file=WindowsPath('sample.robot'),
        line_number=2,
        end_line=2,
        column=1,
        end_column=15,
        severity='W',
        rule_id='DOC02',
        description="Missing documentation in 'this is a test' test case"
    )
    Then return value would look like this:
    # Robocop Report

    ## Violation for file sample.robot in line 2 rule DOC02

    description: Missing documentation in 'this is a test' test case
    start line: 2
    end line: 2
    start column: 1
    end column: 15
    file: C:\\path\\to\\sample.robot
    rule id: DOC02
    severity: WARNING

    All violations reported.

    """
    path_resolved = _resolve_path(path)
    logger.info("Running Robocop on path: '%s'", path_resolved)
    report = await _run_robocop(path_resolved)
    filter_report = _filter_violations(report)
    if not filter_report:
        logger.info("No violations found.")
        return "# Robocop Report\n\nNo violations found."
    logger.info("Dump to markdown...")
    markdown_lines = ["# Robocop Report", ""]
    for item in filter_report:
        markdown_lines.extend(_format_report(item))

    first_violation = filter_report[0] if filter_report else None
    if not first_violation:
        markdown_lines.append("No violations found.")
        return "\n".join(markdown_lines)
    config = _get_config()
    proposed_fix = _get_violation_fix(first_violation, config)
    markdown_lines.extend(
        [
            "",
            "## Proposed fixe for violations",
            "",
            f"The following fix is proposed: {proposed_fix}",
        ],
    )
    if len(filter_report) < len(report):
        markdown_lines.append(f"\nand {len(report) - len(filter_report)} more violations not shown.")
    else:
        markdown_lines.append("\nAll violations reported.")
    return "\n".join(markdown_lines)


def main() -> None:
    "Main to run the robocop-mcp server."
    logger.info("Starting OP Robocop MCP...")
    config = _get_config()
    if config.robocopmcp_config_file:
        logger.info("With %s file.", config.robocopmcp_config_file)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
