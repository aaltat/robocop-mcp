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
from robocop import config as robocop_config  # type: ignore
from robocop.linter.rules import RuleFilter, filter_rules_by_category  # type: ignore
from robocop.linter.runner import RobocopLinter  # type: ignore

logging.basicConfig(format="%(asctime)s %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p", level=logging.INFO)
logger = logging.getLogger("robocop-mcp")


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
    robocop_toml: Path | None = None


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


def _robocop_configured_in_toml(data: dict, pyproject_toml: Path, robocop_toml: Path | None) -> bool:
    if robocop_toml and robocop_toml.is_file():
        logger.info("RoboCop configuration found in %s", robocop_toml)
        return True
    if "tool" in data and "robocop" in data["tool"]:
        logger.info("RoboCop configuration found in %s", pyproject_toml)
        robocop_configured = True
    else:
        logger.info("No RoboCop configuration found in %s", pyproject_toml)
        robocop_configured = False
    return robocop_configured


def _get_robocop_rules() -> list[Rule]:
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


ROBOCOP_RULES = _get_robocop_rules()


def get_config() -> Config:
    pyproject_toml_env = os.environ.get("ROBOCOPMCP_CONFIG_FILE")
    pyproject_toml = Path(pyproject_toml_env).resolve() if pyproject_toml_env else None
    robocop_toml_env = os.environ.get("ROBOCOPMCP_ROBOCOP_CONFIG_FILE")
    robocop_toml = Path(robocop_toml_env).resolve() if robocop_toml_env else None
    if pyproject_toml and pyproject_toml.is_file():
        with pyproject_toml.open("r+b") as file:
            data = tomli.load(file)
        robocop_mcp = data["tool"].get("robocop_mcp", {})
        rules = _get_rule_fixes(ROBOCOP_RULES, robocop_mcp)
        rules = _append_robocop_rules(rules, ROBOCOP_RULES)
        count = _get_violation_count(robocop_mcp, pyproject_toml)
        rule_priority = _get_rule_priority(robocop_mcp, pyproject_toml)
        robocop_configured = _robocop_configured_in_toml(data, pyproject_toml, robocop_toml)
        ignore = robocop_mcp.get("ignore", [])
    else:
        logger.info("No pyproject.toml file found, using default configuration.")
        rules = ROBOCOP_RULES
        count = 20
        rule_priority = []
        robocop_configured = False
        ignore = []
    return Config(pyproject_toml, rules, count, rule_priority, ignore, robocop_configured, robocop_toml)


def resolve_path(path: str | None) -> str:
    if path is None:
        return str(Path())
    return str(Path(path))


def set_robocop_config_file(config: Config, kwargs: dict) -> dict:
    if config.robocop_toml and config.robocop_toml.is_file():
        kwargs["configuration_file"] = config.robocop_toml
    elif config.robocop_configured:
        kwargs["configuration_file"] = config.robocopmcp_config_file
    return kwargs
