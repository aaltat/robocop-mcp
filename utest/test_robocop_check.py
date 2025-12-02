import pytest
from approvaltests.approvals import verify
from types import SimpleNamespace

from src.robocop_mcp.config import Config, get_config, Rule, _get_robocop_rules, _get_user_rule_fixes
from src.robocop_mcp.mcp_check import Violation, get_violation_fix, run_robocop
from src.robocop_mcp.server import (
    get_robocop_report,
)

from .data import (
    TEST_1,
    TOML_FILE,
    ROBOCOP_TOML_FILE,
    TOML_FILE_RULE_AS_FILE,
    TOML_FILE_RULE_NAME_AS_FILE,
    TOML_FILE_RULE_NAME_ALL_AS_FILE,
    TEST_NO_ERRORS,
    TEST_2,
    TEST_3_DUPLICATE_NAMES,
)


TOML_FILE_NO_CONFIG = """
[tool.other_tool]
foo = "bar"
"""

TOML_FILE_NO_ROBOCOP = """
[tool.robocop_mcp]
violation_count = 5
rule_priority = ["DOC02"]

"""
TOML_FILE_IGNORE = """
[tool.robocop_mcp]
ignore = ["DOC02", "DOC03", "COM04"]
rule_priority = ["ARG01"]

"""


@pytest.mark.asyncio
async def test_get_robocop_report_with_sample_file(tmp_path, monkeypatch):
    toml_file = tmp_path / "pyproject.toml"
    toml_file.write_text(TOML_FILE)
    monkeypatch.setenv("ROBOCOPMCP_CONFIG_FILE", str(toml_file))
    robot_file = tmp_path / "sample.robot"
    robot_file.write_text(TEST_1)
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
async def test_get_robocop_report_with_sample_file_and_rule_as_file(tmp_path, monkeypatch):
    toml_file = tmp_path / "pyproject.toml"
    rule_folder = tmp_path / "rules"
    rule_folder.mkdir(parents=True)
    rule_file = rule_folder / "DOC02.md"
    rule_file.write_text("Write documentation for the test case.")
    rule_file_as_str = str(rule_file)
    rule_file_as_str = rule_file_as_str.replace("\\", "/")
    toml_file_text = TOML_FILE_RULE_AS_FILE
    toml_file_text = toml_file_text.replace("REPLACE_ME", f'"{rule_file_as_str}"')
    toml_file.write_text(toml_file_text)
    monkeypatch.setenv("ROBOCOPMCP_CONFIG_FILE", str(toml_file))
    robot_file = tmp_path / "sample.robot"
    robot_file.write_text(TEST_1)
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
async def test_get_robocop_report_with_sample_file_and_rule_name_as_file(tmp_path, monkeypatch):
    toml_file = tmp_path / "pyproject.toml"
    rule_folder = tmp_path / "rules"
    rule_folder.mkdir(parents=True)
    rule_file = rule_folder / "DOC02.md"
    rule_file.write_text("Write documentation for the test case.")
    rule_file_as_str = str(rule_file)
    rule_file_as_str = rule_file_as_str.replace("\\", "/")
    toml_file_text = TOML_FILE_RULE_NAME_AS_FILE
    toml_file_text = toml_file_text.replace("REPLACE_ME", f'"{rule_file_as_str}"')
    toml_file.write_text(toml_file_text)
    monkeypatch.setenv("ROBOCOPMCP_CONFIG_FILE", str(toml_file))
    robot_file = tmp_path / "sample.robot"
    robot_file.write_text(TEST_1)
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
async def test_get_robocop_report_with_rule_priority(tmp_path, monkeypatch):
    toml_file = tmp_path / "pyproject.toml"
    toml_text = TOML_FILE
    toml_text = toml_text.splitlines()
    toml_text.append('rule_priority = ["NAME07"]')
    toml_file.write_text("\n".join(toml_text))
    monkeypatch.setenv("ROBOCOPMCP_CONFIG_FILE", str(toml_file))
    robot_file = tmp_path / "sample.robot"
    robot_file.write_text(TEST_1)
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
async def test_get_robocop_report_with_rule_priority_as_name(tmp_path, monkeypatch):
    toml_file = tmp_path / "pyproject.toml"
    rule_folder = tmp_path / "rules"
    rule_folder.mkdir(parents=True)
    rule_file = rule_folder / "DOC02.md"
    rule_file.write_text("Write documentation for the test case.")
    rule_file_as_str = str(rule_file)
    rule_file_as_str = rule_file_as_str.replace("\\", "/")
    toml_file_text = TOML_FILE_RULE_NAME_ALL_AS_FILE
    toml_file_text = toml_file_text.replace("REPLACE_ME", f'"{rule_file_as_str}"')
    toml_file.write_text(toml_file_text)
    monkeypatch.setenv("ROBOCOPMCP_CONFIG_FILE", str(toml_file))
    robot_file = tmp_path / "sample.robot"
    robot_file.write_text(TEST_1)
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
async def test_get_robocop_report_with_rule_priority_as_name_and_fix_as_rule_id(tmp_path, monkeypatch):
    toml_file = tmp_path / "pyproject.toml"
    rule_folder = tmp_path / "rules"
    rule_folder.mkdir(parents=True)
    rule_file = rule_folder / "DOC02.md"
    rule_file.write_text("Write documentation for the test case.")
    rule_file_as_str = str(rule_file)
    rule_file_as_str = rule_file_as_str.replace("\\", "/")
    toml_file_text = TOML_FILE_RULE_NAME_ALL_AS_FILE
    toml_file_text = toml_file_text.replace(
        "missing-doc-test-case = REPLACE_ME", f'DOC02 = "{rule_file_as_str}"'
    )
    toml_file.write_text(toml_file_text)
    monkeypatch.setenv("ROBOCOPMCP_CONFIG_FILE", str(toml_file))
    robot_file = tmp_path / "sample.robot"
    robot_file.write_text(TEST_1)
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
async def test_get_robocop_report_with_rule_priority_not_found(tmp_path, monkeypatch):
    toml_file = tmp_path / "pyproject.toml"
    toml_text = TOML_FILE
    toml_text = toml_text.splitlines()
    toml_text.append('rule_priority = ["INVALID9876123"]')
    toml_file.write_text("\n".join(toml_text))
    monkeypatch.setenv("ROBOCOPMCP_CONFIG_FILE", str(toml_file))
    robot_file = tmp_path / "sample.robot"
    robot_file.write_text(TEST_1)
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
async def test_get_robocop_report_no_violations(tmp_path, monkeypatch):
    toml_file = tmp_path / "pyproject.toml"
    toml_file.write_text(TOML_FILE)
    monkeypatch.setenv("ROBOCOPMCP_CONFIG_FILE", str(toml_file))
    robot_file = tmp_path / "sample.robot"
    robot_file.write_text(TEST_NO_ERRORS)
    result = await get_robocop_report(str(robot_file))
    lines = [line for line in result.splitlines() if not line.startswith("file")]
    lines_filtered = "\n".join(lines)
    verify(lines_filtered)


@pytest.mark.asyncio
async def test_get_robocop_report_no_config(tmp_path, monkeypatch):
    toml_file = tmp_path / "pyproject.toml"
    toml_file.write_text(TOML_FILE_NO_CONFIG)
    monkeypatch.setenv("ROBOCOPMCP_CONFIG_FILE", str(toml_file))
    robot_file = tmp_path / "sample.robot"
    robot_file.write_text(TEST_1)
    result = await get_robocop_report(str(robot_file))
    lines = [line for line in result.splitlines() if not line.startswith("file")]
    lines_filtered = "\n".join(lines)
    verify(lines_filtered)


@pytest.mark.asyncio
async def test_get_robocop_report_no_config_file(tmp_path, monkeypatch):
    toml_file = tmp_path / "nothere.toml"
    monkeypatch.setenv("ROBOCOPMCP_CONFIG_FILE", str(toml_file))
    robot_file = tmp_path / "sample.robot"
    robot_file.write_text(TEST_1)
    result = await get_robocop_report(str(robot_file))
    lines = [line for line in result.splitlines() if not line.startswith("file")]
    lines_filtered = "\n".join(lines)
    verify(lines_filtered)


@pytest.mark.asyncio
async def test_get_robocop_report_no_robocop_config(tmp_path, monkeypatch):
    toml_file = tmp_path / "pyproject.toml"
    toml_file.write_text(TOML_FILE_NO_ROBOCOP)
    monkeypatch.setenv("ROBOCOPMCP_CONFIG_FILE", str(toml_file))
    robot_file = tmp_path / "sample.robot"
    robot_file.write_text(TEST_1)
    result = await get_robocop_report(str(robot_file))
    assert "file: " in result
    assert "sample.robot" in result


@pytest.mark.asyncio
async def test_get_robocop_report_invalid_config(tmp_path, monkeypatch):
    toml_file = tmp_path / "pyproject.toml"
    config = TOML_FILE_NO_ROBOCOP
    config = config.replace("violation_count = 5", 'violation_count = "invalid_value"')
    toml_file.write_text(config)
    monkeypatch.setenv("ROBOCOPMCP_CONFIG_FILE", str(toml_file))
    robot_file = tmp_path / "sample.robot"
    robot_file.write_text(TEST_1)
    result = await get_robocop_report(str(robot_file))
    assert "file: " in result
    assert "sample.robot" in result

    config = TOML_FILE_NO_ROBOCOP
    config = config.replace('rule_priority = ["DOC02"]', 'rule_priority = "DOC02"')
    toml_file.write_text(config)
    result = await get_robocop_report(str(robot_file))
    assert "file: " in result
    assert "sample.robot" in result


@pytest.mark.asyncio
async def test_get_robocop_report_ignore(tmp_path, monkeypatch):
    toml_file = tmp_path / "pyproject.toml"
    toml_file.write_text(TOML_FILE_IGNORE)
    monkeypatch.setenv("ROBOCOPMCP_CONFIG_FILE", str(toml_file))
    robot_file = tmp_path / "sample.robot"
    robot_file.write_text(TEST_1)
    result = await get_robocop_report(str(robot_file))
    lines = [line for line in result.splitlines() if not line.startswith("file")]
    lines_filtered = "\n".join(lines)
    verify(lines_filtered)


@pytest.mark.asyncio
async def test_get_robocop_report_ignore_as_name(tmp_path, monkeypatch):
    toml_file = tmp_path / "pyproject.toml"
    toml_file_text = TOML_FILE_IGNORE
    toml_file_text = toml_file_text.replace(
        'ignore = ["DOC02", "DOC03", "COM04"]',
        "ignore = ['missing-doc-test-case', 'missing-doc-suite', 'ignored-data']",
    )
    toml_file.write_text(toml_file_text)
    monkeypatch.setenv("ROBOCOPMCP_CONFIG_FILE", str(toml_file))
    robot_file = tmp_path / "sample.robot"
    robot_file.write_text(TEST_1)
    result = await get_robocop_report(str(robot_file))
    lines = [line for line in result.splitlines() if not line.startswith("file")]
    lines_filtered = "\n".join(lines)
    verify(lines_filtered)


@pytest.mark.asyncio
async def test_get_robocop_report_robocop_toml(tmp_path, monkeypatch):
    toml_file = tmp_path / "pyproject.toml"
    toml_file.write_text(TOML_FILE)
    monkeypatch.setenv("ROBOCOPMCP_CONFIG_FILE", str(toml_file))
    robocop_toml_file = tmp_path / "robocop.toml"
    robocop_toml_file.write_text(ROBOCOP_TOML_FILE)
    monkeypatch.setenv("ROBOCOPMCP_ROBOCOP_CONFIG_FILE", str(robocop_toml_file))
    robot_file = tmp_path / "sample.robot"
    robot_file.write_text(TEST_1)
    result = await get_robocop_report(str(robot_file))
    lines = [line for line in result.splitlines() if not line.startswith("file")]
    lines_filtered = "\n".join(lines)
    verify(lines_filtered)


@pytest.mark.asyncio
async def test_get_robocop_report_no_robocopmcp_toml(tmp_path, monkeypatch):
    robocop_toml_file = tmp_path / "robocop.toml"
    robocop_toml_file.write_text(ROBOCOP_TOML_FILE)
    monkeypatch.setenv("ROBOCOPMCP_ROBOCOP_CONFIG_FILE", str(robocop_toml_file))
    robot_file = tmp_path / "sample.robot"
    robot_file.write_text(TEST_1)
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
async def test_run_robocop_with_sample_file(tmp_path, monkeypatch):
    toml_file = tmp_path / "pyproject.toml"
    toml_file.write_text(TOML_FILE)
    monkeypatch.setenv("ROBOCOPMCP_CONFIG_FILE", str(toml_file))
    robot_file = tmp_path / "sample.robot"
    robot_file.write_text(TEST_2)
    result = await run_robocop(str(robot_file))
    assert isinstance(result, list)
    assert all(isinstance(v, Violation) for v in result)
    # Optionally check fields of the first violation
    v = result[0]
    assert hasattr(v, "file")
    assert hasattr(v, "rule_id")
    assert hasattr(v, "description")


@pytest.mark.asyncio
async def test_get_robocop_report_no_fix_found(tmp_path):
    robot_file = tmp_path / "sample.robot"
    robot_file.write_text(TEST_1)

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
async def test_get_violation_fix_returns_instruction(tmp_path):
    sample_file = tmp_path / "sample.robot"
    sample_file.write_text(TEST_1)
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
async def test_get_violation_fix_reads_instruction_file(tmp_path):
    sample_file = tmp_path / "sample.robot"
    sample_file.write_text(TEST_1)
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
async def test_get_violation_fix_returns_default_when_not_found(tmp_path):
    sample_file = tmp_path / "sample.robot"
    sample_file.write_text(TEST_1)
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
async def test_get_violation_fix_returns_predefined_fix(tmp_path):
    sample_file = tmp_path / "sample.robot"
    sample_file.write_text(TEST_3_DUPLICATE_NAMES)
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
async def test_get_violation_fix_returns_custom_rule_instead_of_predefined_fix(tmp_path):
    sample_file = tmp_path / "sample.robot"
    sample_file.write_text(TEST_3_DUPLICATE_NAMES)
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
