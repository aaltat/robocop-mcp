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

from dataclasses import dataclass
from pathlib import Path

from robocop.linter.diagnostics import Diagnostic  # type: ignore
from robocop.run import check_files  # type: ignore

from .config import Config, get_config, logger, set_robocop_config_file


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


async def run_robocop(path: str) -> list[Violation]:
    sources = [Path(path)]
    kwargs = {"sources": sources, "return_result": True, "silent": True}
    config = get_config()
    kwargs = set_robocop_config_file(config, kwargs)
    logger.info("Running Robocop check_files with kwargs: %s", kwargs)
    result = check_files(**kwargs)
    if result is None:
        return []
    return _convert_to_violations(result)


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


def filter_violations(violations: list[Violation]) -> list[Violation]:
    config = get_config()
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


def format_report(violation: Violation) -> list[str]:
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


def get_violation_fix(violation: Violation, config: Config) -> str:
    rule_id = violation.rule_id
    if rule_id in config.user_rules:
        rule_fix = config.user_rules[rule_id]
        if _is_file(rule_fix.instruction):
            with Path(rule_fix.instruction).open("r") as file:
                return file.read()
        return rule_fix.instruction
    if rule_id in config.predefined_fixes:
        rule_fix = config.predefined_fixes[rule_id]
        if _is_file(rule_fix.instruction):
            with Path(rule_fix.instruction).open("r") as file:
                return file.read()
        return rule_fix.instruction
    if rule_id in config.robocop_rules:
        rule_fix = config.robocop_rules[rule_id]
        return rule_fix.instruction
    return "No solution proposed fix found"
