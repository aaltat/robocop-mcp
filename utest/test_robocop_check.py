import pytest
from approvaltests.approvals import verify
from types import SimpleNamespace

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
from src.robocop_mcp.mcp_check import Violation, get_violation_fix, run_robocop
from src.robocop_mcp.server import (
    get_robocop_report,
)


@pytest.mark.asyncio
async def test_get_robocop_report_with_sample_file(tmp_path, monkeypatch, test_1, toml_file_content):
    toml_file = tmp_path / "pyproject.toml"
    toml_file.write_text(toml_file_content)
    monkeypatch.setenv("ROBOCOPMCP_CONFIG_FILE", str(toml_file))
    robot_file = tmp_path / "sample.robot"
    robot_file.write_text(test_1)
    result = await get_robocop_report(str(robot_file))
    lines = [line for line in result.splitlines() if not line.startswith("file")]
    lines_filtered = "\n".join(lines)
    verify(lines_filtered)
    file_line = [line for line in result.splitlines() if line.startswith("file")]
    assert len(file_line) == 1
    line = file_line[0]
    assert "file: " in line
    assert "sample.robot" in line


@pytest.mark.asyncio
async def test_get_robocop_report_with_sample_file_and_rule_as_file(
    tmp_path, monkeypatch, test_1, toml_file_rule_as_file
):
    toml_file = tmp_path / "pyproject.toml"
    rule_folder = tmp_path / "rules"
    rule_folder.mkdir(parents=True)
    rule_file = rule_folder / "DOC02.md"
    rule_file.write_text("Write documentation for the test case.")
    rule_file_as_str = str(rule_file)
    rule_file_as_str = rule_file_as_str.replace("\\", "/")
    toml_file_text = toml_file_rule_as_file
    toml_file_text = toml_file_text.replace("REPLACE_ME", f'"{rule_file_as_str}"')
    toml_file.write_text(toml_file_text)
    monkeypatch.setenv("ROBOCOPMCP_CONFIG_FILE", str(toml_file))
    robot_file = tmp_path / "sample.robot"
    robot_file.write_text(test_1)
    result = await get_robocop_report(str(robot_file))
    lines = [line for line in result.splitlines() if not line.startswith("file")]
    lines_filtered = "\n".join(lines)
    verify(lines_filtered)
    file_line = [line for line in result.splitlines() if line.startswith("file")]
    assert len(file_line) == 1
    line = file_line[0]
    assert "file: " in line
    assert "sample.robot" in line


@pytest.mark.asyncio
async def test_get_robocop_report_with_sample_file_and_rule_name_as_file(
    tmp_path, monkeypatch, test_1, toml_file_rule_name_as_file
):
    toml_file = tmp_path / "pyproject.toml"
    rule_folder = tmp_path / "rules"
    rule_folder.mkdir(parents=True)
    rule_file = rule_folder / "DOC02.md"
    rule_file.write_text("Write documentation for the test case.")
    rule_file_as_str = str(rule_file)
    rule_file_as_str = rule_file_as_str.replace("\\", "/")
    toml_file_text = toml_file_rule_name_as_file
    toml_file_text = toml_file_text.replace("REPLACE_ME", f'"{rule_file_as_str}"')
    toml_file.write_text(toml_file_text)
    monkeypatch.setenv("ROBOCOPMCP_CONFIG_FILE", str(toml_file))
    robot_file = tmp_path / "sample.robot"
    robot_file.write_text(test_1)
    result = await get_robocop_report(str(robot_file))
    lines = [line for line in result.splitlines() if not line.startswith("file")]
    lines_filtered = "\n".join(lines)
    verify(lines_filtered)
    file_line = [line for line in result.splitlines() if line.startswith("file")]
    assert len(file_line) == 1
    line = file_line[0]
    assert "file: " in line
    assert "sample.robot" in line


@pytest.mark.asyncio
async def test_get_robocop_report_with_rule_priority(tmp_path, monkeypatch, test_1, toml_file_content):
    toml_file = tmp_path / "pyproject.toml"
    toml_text = toml_file_content
    toml_text = toml_text.splitlines()
    toml_text.append('rule_priority = ["NAME07"]')
    toml_file.write_text("\n".join(toml_text))
    monkeypatch.setenv("ROBOCOPMCP_CONFIG_FILE", str(toml_file))
    robot_file = tmp_path / "sample.robot"
    robot_file.write_text(test_1)
    result = await get_robocop_report(str(robot_file))
    lines = [line for line in result.splitlines() if not line.startswith("file")]
    lines_filtered = "\n".join(lines)
    verify(lines_filtered)
    file_line = [line for line in result.splitlines() if line.startswith("file")]
    assert len(file_line) == 1
    line = file_line[0]
    assert "file: " in line
    assert "sample.robot" in line


@pytest.mark.asyncio
async def test_get_robocop_report_with_rule_priority_as_name(
    tmp_path, monkeypatch, test_1, toml_file_rule_name_all_as_file
):
    toml_file = tmp_path / "pyproject.toml"
    rule_folder = tmp_path / "rules"
    rule_folder.mkdir(parents=True)
    rule_file = rule_folder / "DOC02.md"
    rule_file.write_text("Write documentation for the test case.")
    rule_file_as_str = str(rule_file)
    rule_file_as_str = rule_file_as_str.replace("\\", "/")
    toml_file_text = toml_file_rule_name_all_as_file
    toml_file_text = toml_file_text.replace("REPLACE_ME", f'"{rule_file_as_str}"')
    toml_file.write_text(toml_file_text)
    monkeypatch.setenv("ROBOCOPMCP_CONFIG_FILE", str(toml_file))
    robot_file = tmp_path / "sample.robot"
    robot_file.write_text(test_1)
    result = await get_robocop_report(str(robot_file))
    lines = [line for line in result.splitlines() if not line.startswith("file")]
    lines_filtered = "\n".join(lines)
    verify(lines_filtered)
    file_line = [line for line in result.splitlines() if line.startswith("file")]
    assert len(file_line) == 1
    line = file_line[0]
    assert "file: " in line
    assert "sample.robot" in line


@pytest.mark.asyncio
async def test_get_robocop_report_with_rule_priority_as_name_and_fix_as_rule_id(
    tmp_path, monkeypatch, test_1, toml_file_rule_name_all_as_file
):
    toml_file = tmp_path / "pyproject.toml"
    rule_folder = tmp_path / "rules"
    rule_folder.mkdir(parents=True)
    rule_file = rule_folder / "DOC02.md"
    rule_file.write_text("Write documentation for the test case.")
    rule_file_as_str = str(rule_file)
    rule_file_as_str = rule_file_as_str.replace("\\", "/")
    toml_file_text = toml_file_rule_name_all_as_file
    toml_file_text = toml_file_text.replace(
        "missing-doc-test-case = REPLACE_ME", f'DOC02 = "{rule_file_as_str}"'
    )
    toml_file.write_text(toml_file_text)
    monkeypatch.setenv("ROBOCOPMCP_CONFIG_FILE", str(toml_file))
    robot_file = tmp_path / "sample.robot"
    robot_file.write_text(test_1)
    result = await get_robocop_report(str(robot_file))
    lines = [line for line in result.splitlines() if not line.startswith("file")]
    lines_filtered = "\n".join(lines)
    verify(lines_filtered)
    file_line = [line for line in result.splitlines() if line.startswith("file")]
    assert len(file_line) == 1
    line = file_line[0]
    assert "file: " in line
    assert "sample.robot" in line


@pytest.mark.asyncio
async def test_get_robocop_report_with_rule_priority_not_found(
    tmp_path, monkeypatch, test_1, toml_file_content
):
    toml_file = tmp_path / "pyproject.toml"
    toml_text = toml_file_content
    toml_text = toml_text.splitlines()
    toml_text.append('rule_priority = ["INVALID9876123"]')
    toml_file.write_text("\n".join(toml_text))
    monkeypatch.setenv("ROBOCOPMCP_CONFIG_FILE", str(toml_file))
    robot_file = tmp_path / "sample.robot"
    robot_file.write_text(test_1)
    result = await get_robocop_report(str(robot_file))
    lines = [line for line in result.splitlines() if not line.startswith("file")]
    lines_filtered = "\n".join(lines)
    verify(lines_filtered)
    file_line = [line for line in result.splitlines() if line.startswith("file")]
    assert len(file_line) == 1
    line = file_line[0]
    assert "file: " in line
    assert "sample.robot" in line


@pytest.mark.asyncio
async def test_get_robocop_report_no_violations(tmp_path, monkeypatch, test_no_errors, toml_file_content):
    toml_file = tmp_path / "pyproject.toml"
    toml_file.write_text(toml_file_content)
    monkeypatch.setenv("ROBOCOPMCP_CONFIG_FILE", str(toml_file))
    robot_file = tmp_path / "sample.robot"
    robot_file.write_text(test_no_errors)
    result = await get_robocop_report(str(robot_file))
    lines = [line for line in result.splitlines() if not line.startswith("file")]
    lines_filtered = "\n".join(lines)
    verify(lines_filtered)


@pytest.mark.asyncio
async def test_get_robocop_report_no_config(tmp_path, monkeypatch, test_1, toml_file_no_config):
    toml_file = tmp_path / "pyproject.toml"
    toml_file.write_text(toml_file_no_config)
    monkeypatch.setenv("ROBOCOPMCP_CONFIG_FILE", str(toml_file))
    robot_file = tmp_path / "sample.robot"
    robot_file.write_text(test_1)
    result = await get_robocop_report(str(robot_file))
    lines = [line for line in result.splitlines() if not line.startswith("file")]
    lines_filtered = "\n".join(lines)
    verify(lines_filtered)


@pytest.mark.asyncio
async def test_get_robocop_report_no_config_file(tmp_path, monkeypatch, test_1):
    toml_file = tmp_path / "nothere.toml"
    monkeypatch.setenv("ROBOCOPMCP_CONFIG_FILE", str(toml_file))
    robot_file = tmp_path / "sample.robot"
    robot_file.write_text(test_1)
    result = await get_robocop_report(str(robot_file))
    lines = [line for line in result.splitlines() if not line.startswith("file")]
    lines_filtered = "\n".join(lines)
    verify(lines_filtered)


@pytest.mark.asyncio
async def test_get_robocop_report_no_robocop_config(tmp_path, monkeypatch, test_1, toml_file_no_robocop):
    toml_file = tmp_path / "pyproject.toml"
    toml_file.write_text(toml_file_no_robocop)
    monkeypatch.setenv("ROBOCOPMCP_CONFIG_FILE", str(toml_file))
    robot_file = tmp_path / "sample.robot"
    robot_file.write_text(test_1)
    result = await get_robocop_report(str(robot_file))
    assert "file: " in result
    assert "sample.robot" in result


@pytest.mark.asyncio
async def test_get_robocop_report_invalid_config(tmp_path, monkeypatch, test_1, toml_file_no_robocop):
    toml_file = tmp_path / "pyproject.toml"
    config = toml_file_no_robocop
    config = config.replace("violation_count = 5", 'violation_count = "invalid_value"')
    toml_file.write_text(config)
    monkeypatch.setenv("ROBOCOPMCP_CONFIG_FILE", str(toml_file))
    robot_file = tmp_path / "sample.robot"
    robot_file.write_text(test_1)
    result = await get_robocop_report(str(robot_file))
    assert "file: " in result
    assert "sample.robot" in result

    config = toml_file_no_robocop
    config = config.replace('rule_priority = ["DOC02"]', 'rule_priority = "DOC02"')
    toml_file.write_text(config)
    result = await get_robocop_report(str(robot_file))
    assert "file: " in result
    assert "sample.robot" in result


@pytest.mark.asyncio
async def test_get_robocop_report_ignore(tmp_path, monkeypatch, test_1, toml_file_ignore):
    toml_file = tmp_path / "pyproject.toml"
    toml_file.write_text(toml_file_ignore)
    monkeypatch.setenv("ROBOCOPMCP_CONFIG_FILE", str(toml_file))
    robot_file = tmp_path / "sample.robot"
    robot_file.write_text(test_1)
    result = await get_robocop_report(str(robot_file))
    lines = [line for line in result.splitlines() if not line.startswith("file")]
    lines_filtered = "\n".join(lines)
    verify(lines_filtered)


@pytest.mark.asyncio
async def test_get_robocop_report_ignore_as_name(tmp_path, monkeypatch, test_1, toml_file_ignore):
    toml_file = tmp_path / "pyproject.toml"
    toml_file_text = toml_file_ignore
    toml_file_text = toml_file_text.replace(
        'ignore = ["DOC02", "DOC03", "COM04"]',
        "ignore = ['missing-doc-test-case', 'missing-doc-suite', 'ignored-data']",
    )
    toml_file.write_text(toml_file_text)
    monkeypatch.setenv("ROBOCOPMCP_CONFIG_FILE", str(toml_file))
    robot_file = tmp_path / "sample.robot"
    robot_file.write_text(test_1)
    result = await get_robocop_report(str(robot_file))
    lines = [line for line in result.splitlines() if not line.startswith("file")]
    lines_filtered = "\n".join(lines)
    verify(lines_filtered)


@pytest.mark.asyncio
async def test_get_robocop_report_robocop_toml(
    tmp_path, monkeypatch, test_1, toml_file_content, robocop_toml_file_content
):
    toml_file = tmp_path / "pyproject.toml"
    toml_file.write_text(toml_file_content)
    monkeypatch.setenv("ROBOCOPMCP_CONFIG_FILE", str(toml_file))
    robocop_toml_file = tmp_path / "robocop.toml"
    robocop_toml_file.write_text(robocop_toml_file_content)
    monkeypatch.setenv("ROBOCOPMCP_ROBOCOP_CONFIG_FILE", str(robocop_toml_file))
    robot_file = tmp_path / "sample.robot"
    robot_file.write_text(test_1)
    result = await get_robocop_report(str(robot_file))
    lines = [line for line in result.splitlines() if not line.startswith("file")]
    lines_filtered = "\n".join(lines)
    verify(lines_filtered)


@pytest.mark.asyncio
async def test_get_robocop_report_no_robocopmcp_toml(
    tmp_path, monkeypatch, test_1, robocop_toml_file_content
):
    robocop_toml_file = tmp_path / "robocop.toml"
    robocop_toml_file.write_text(robocop_toml_file_content)
    monkeypatch.setenv("ROBOCOPMCP_ROBOCOP_CONFIG_FILE", str(robocop_toml_file))
    robot_file = tmp_path / "sample.robot"
    robot_file.write_text(test_1)
    result = await get_robocop_report(str(robot_file))
    lines = [line for line in result.splitlines() if not line.startswith("file")]
    lines_filtered = "\n".join(lines)
    verify(lines_filtered)


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
async def test_run_robocop_with_sample_file(tmp_path, monkeypatch, test_2, toml_file_content):
    toml_file = tmp_path / "pyproject.toml"
    toml_file.write_text(toml_file_content)
    monkeypatch.setenv("ROBOCOPMCP_CONFIG_FILE", str(toml_file))
    robot_file = tmp_path / "sample.robot"
    robot_file.write_text(test_2)
    result = await run_robocop(str(robot_file))
    assert isinstance(result, list)
    assert all(isinstance(v, Violation) for v in result)
    # Optionally check fields of the first violation
    v = result[0]
    assert hasattr(v, "file")
    assert hasattr(v, "rule_id")
    assert hasattr(v, "description")


@pytest.mark.asyncio
async def test_get_robocop_report_no_fix_found(tmp_path, test_1):
    robot_file = tmp_path / "sample.robot"
    robot_file.write_text(test_1)

    mock_violation = Violation(
        file=robot_file,
        start_line=2,
        end_line=2,
        start_column=1,
        end_column=10,
        severity="W",
        rule_id="NotHere001",
        description="Missing documentation in 'Test Case' test case",
    )
    config = get_config()
    result = get_violation_fix(mock_violation, config)
    assert result == "No solution proposed fix found"


@pytest.mark.asyncio
async def test_get_violation_fix_returns_instruction(tmp_path, test_1):
    sample_file = tmp_path / "sample.robot"
    sample_file.write_text(test_1)
    violation = Violation(
        file=sample_file,
        start_line=1,
        end_line=1,
        start_column=1,
        end_column=1,
        severity="W",
        rule_id="DOC01",
        description="Missing documentation",
    )
    config = SimpleNamespace(
        user_rules={
            "DOC01": Rule(
                rule_id="DOC01", instruction="Add documentation to the test case.", name="missing-doc-keyword"
            )
        },
        predefined_fixes={},
    )

    result = get_violation_fix(violation, config)

    assert result == "Add documentation to the test case."


@pytest.mark.asyncio
async def test_get_violation_fix_reads_instruction_file(tmp_path, test_1):
    sample_file = tmp_path / "sample.robot"
    sample_file.write_text(test_1)
    instruction_file = tmp_path / "instruction.md"
    instruction_file.write_text("Detailed fix instructions.")
    violation = Violation(
        file=sample_file,
        start_line=1,
        end_line=1,
        start_column=1,
        end_column=1,
        severity="W",
        rule_id="DOC02",
        description="Another issue",
    )
    config = SimpleNamespace(
        user_rules={
            "DOC02": Rule(rule_id="DOC02", instruction=str(instruction_file), name="missing-doc-keyword")
        },
        predefined_fixes={},
        robocop_rules={},
    )

    result = get_violation_fix(violation, config)

    assert result == "Detailed fix instructions."


@pytest.mark.asyncio
async def test_get_violation_fix_returns_default_when_not_found(tmp_path, test_1):
    sample_file = tmp_path / "sample.robot"
    sample_file.write_text(test_1)
    violation = Violation(
        file=sample_file,
        start_line=1,
        end_line=1,
        start_column=1,
        end_column=1,
        severity="W",
        rule_id="DOC03",
        description="Unmatched issue",
    )
    config = SimpleNamespace(
        user_rules={
            "DOC01": Rule(rule_id="DOC01", instruction="Some instruction", name="missing-doc-keyword")
        },
        predefined_fixes={},
        robocop_rules={},
    )

    result = get_violation_fix(violation, config)

    assert result == "No solution proposed fix found"


@pytest.mark.asyncio
async def test_get_violation_fix_returns_predefined_fix(tmp_path, test_3_duplicate_names):
    sample_file = tmp_path / "sample.robot"
    sample_file.write_text(test_3_duplicate_names)
    violation = Violation(
        file=sample_file,
        start_line=1,
        end_line=1,
        start_column=1,
        end_column=1,
        severity="W",
        rule_id="DUP01",
        description="There are duplicate test cases",
    )
    fix_proposal = "With a duplicate test names add a running index index in the test name with three digits."
    config = SimpleNamespace(
        user_rules={
            "DOC01": Rule(rule_id="DOC01", instruction="Some instruction", name="missing-doc-keyword")
        },
        predefined_fixes={
            "DUP01": Rule(
                rule_id="DUP01",
                instruction=fix_proposal,
                name="duplicated-test-cases",
            )
        },
        robocop_rules={},
    )
    result = get_violation_fix(violation, config)
    assert fix_proposal == result


@pytest.mark.asyncio
async def test_get_violation_fix_returns_custom_rule_instead_of_predefined_fix(
    tmp_path, test_3_duplicate_names
):
    sample_file = tmp_path / "sample.robot"
    sample_file.write_text(test_3_duplicate_names)
    violation = Violation(
        file=sample_file,
        start_line=1,
        end_line=1,
        start_column=1,
        end_column=1,
        severity="W",
        rule_id="DUP01",
        description="There are duplicate test cases",
    )
    fix_proposal = "With a duplicate test names add a running index index in the test name with three digits."
    config = SimpleNamespace(
        user_rules={
            "DUP01": Rule(rule_id="DUP01", instruction="Some instruction", name="duplicated-test-case")
        },
        predefined_fixes={
            "DUP01": Rule(
                rule_id="DUP01",
                instruction=fix_proposal,
                name="duplicated-test-cases",
            )
        },
        robocop_rules={},
    )
    result = get_violation_fix(violation, config)
    assert result == "Some instruction"


def test_get_user_rule_fixes_populates_rules():
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


def test_get_robocop_rules_returns_rule_mapping():
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


def test_get_robocop_rule_name_defaults_to_lowercase():
    result = _get_robocop_rule_name("UNKNOWN_RULE_ID")
    assert result == "unknown_rule_id"


def test_get_rule_ignore_converts_string_to_list(tmp_path):
    config = {"ignore": "DOC02"}
    result = _get_rule_ignore(config, tmp_path / "pyproject.toml")

    assert result == ["DOC02"]


@pytest.mark.asyncio
async def test_get_violation_fix_reads_predefined_instruction_file(tmp_path, test_1):
    sample_file = tmp_path / "sample.robot"
    sample_file.write_text(test_1)
    instruction_file = tmp_path / "predefined_fix.md"
    instruction_file.write_text("Predefined file instruction.")
    violation = Violation(
        file=sample_file,
        start_line=1,
        end_line=1,
        start_column=1,
        end_column=1,
        severity="W",
        rule_id="DOC02",
        description="Needs predefined fix",
    )
    config = SimpleNamespace(
        user_rules={},
        predefined_fixes={
            "DOC02": Rule(
                rule_id="DOC02",
                instruction=str(instruction_file),
                name="missing-doc-keyword",
            )
        },
        robocop_rules={},
    )

    result = get_violation_fix(violation, config)

    assert result == "Predefined file instruction."


def test_get_predefined_fixes_reads_rule_file(tmp_path, monkeypatch):
    rule_file = tmp_path / "UNKNOWN_RULE.md"
    rule_file.write_text("Instruction text.\n")
    monkeypatch.setattr(config_module, "get_rules_files", lambda: [rule_file])

    result = _get_predefined_fixes()
    assert isinstance(result, dict)
    assert "UNKNOWN" in result
    assert result["UNKNOWN"].rule_id == "UNKNOWN"
    assert result["UNKNOWN"].instruction == "Instruction text."
    assert result["UNKNOWN"].name == "unknown"
