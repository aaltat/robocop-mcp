import pytest

import src.robocop_mcp.config as config_module
from src.robocop_mcp.config import (
    Config,
    _get_rule_ignore,
    get_config,
    Rule,
    _get_robocop_rules,
    _get_user_rule_fixes,
    _get_robocop_rule_name,
    _get_predefined_fixes,
)
from src.robocop_mcp.mcp_check import Violation, run_robocop


def test_get_config_default(monkeypatch):
    monkeypatch.delenv("ROBOCOPMCP_CONFIG_FILE", raising=False)
    config = get_config()
    assert isinstance(config, Config)
    assert config.robocopmcp_config_file is None
    assert isinstance(config.user_rules, dict)
    assert isinstance(config.predefined_fixes, dict)
    assert "README" not in config.predefined_fixes
    assert isinstance(config.robocop_rules, dict)
    assert config.violation_count == 20


def test_get_config_with_toml(tmp_path, monkeypatch):
    toml_file = tmp_path / "pyproject.toml"
    toml_file.write_text('[tool.robocop_mcp]\nDOC02 = "Missing documentation"\nviolation_count = 5\n')
    monkeypatch.setenv("ROBOCOPMCP_CONFIG_FILE", str(toml_file))
    config = get_config()
    assert config.robocopmcp_config_file == toml_file.resolve()
    assert config.violation_count == 5
    assert any(rule.rule_id == "DOC02" for rule in config.user_rules.values())


@pytest.mark.asyncio
async def test_run_robocop_returns_violation_objects(tmp_path, monkeypatch, test_2, toml_file_content):
    toml_file = tmp_path / "pyproject.toml"
    toml_file.write_text(toml_file_content)
    monkeypatch.setenv("ROBOCOPMCP_CONFIG_FILE", str(toml_file))
    robot_file = tmp_path / "sample.robot"
    robot_file.write_text(test_2)
    result = await run_robocop(str(robot_file))
    assert isinstance(result, list)
    assert all(isinstance(v, Violation) for v in result)
    v = result[0]
    assert hasattr(v, "file")
    assert hasattr(v, "rule_id")
    assert hasattr(v, "description")


def test_get_user_rule_fixes_creates_rule_objects_from_config():
    assert _get_user_rule_fixes({}) == {}
    config = {"doc01": "Add docs", "ARG05": "Update arguments"}
    result = _get_user_rule_fixes(config)

    assert set(result.keys()) == {"DOC01", "ARG05"}
    assert isinstance(result["DOC01"], Rule)
    assert result["DOC01"].instruction == "Add docs"
    assert result["ARG05"].instruction == "Update arguments"
    config = {"doc01": "Add docs", "ARG05": "Update arguments", "violation_count": 10}
    result = _get_user_rule_fixes(config)
    assert set(result.keys()) == {"DOC01", "ARG05"}


def test_get_robocop_rules_loads_builtin_rule_definitions():
    rules = _get_robocop_rules()
    assert isinstance(rules, dict)
    assert rules
    for rule_id, rule in rules.items():
        if rule_id == "DOC01":
            assert rule.instruction.startswith("\nKeyword without documentation.")
            assert rule.name == "missing-doc-keyword"
        assert isinstance(rule, Rule)
        assert rule.rule_id == rule_id
        assert isinstance(rule.instruction, str)
        assert isinstance(rule.name, str)


def test_get_robocop_rule_name_converts_unknown_to_lowercase():
    result = _get_robocop_rule_name("UNKNOWN_RULE_ID")
    assert result == "unknown_rule_id"


def test_get_rule_ignore_normalizes_string_to_list_format(tmp_path):
    config = {"ignore": "DOC02"}
    result = _get_rule_ignore(config, tmp_path / "pyproject.toml")

    assert result == ["DOC02"]


def test_get_predefined_fixes_discovers_rules_from_files(tmp_path, monkeypatch):
    rule_file = tmp_path / "UNKNOWN_RULE.md"
    rule_file.write_text("Instruction text.\n")
    monkeypatch.setattr(config_module, "get_rules_files", lambda: [rule_file])

    result = _get_predefined_fixes()
    assert isinstance(result, dict)
    assert "UNKNOWN" in result
    assert result["UNKNOWN"].rule_id == "UNKNOWN"
    assert result["UNKNOWN"].instruction == "Instruction text."
    assert result["UNKNOWN"].name == "unknown"
