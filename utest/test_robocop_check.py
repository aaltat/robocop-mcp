import pytest
from approvaltests.approvals import verify

from src.robocop_mcp.config import Config, get_config
from src.robocop_mcp.mcp_check import Violation, run_robocop
from src.robocop_mcp.server import (
    get_robocop_report,
)


TOML_FILE = """
[tool.robocop]
language = ["en"]
[tool.robocop_mcp]
DOC02 = "Missing documentation"
violation_count = 5
"""

TOML_FILE_RULE_AS_FILE = """
[tool.robocop_mcp]
DOC02 = REPLACE_ME
violation_count = 5
rule_priority = ["DOC02"]

[tool.robocop]
language = ["en"]

"""

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


ROBOCOP_TOML_FILE = """
[lint]
ignore = ["DOC02", "DOC03", "COM04", "COM04"]
"""


TEST_1 = """
*** Test Cases ***
this is a test
    Log    Hello, World!"""

TEST_2 = """
*** Test Cases ***
Example Test 1
    Log    Hello, World!
Example Test 2
    Log    Hello, World!"""

TEST_NO_ERRORS = """\
*** Settings ***
Documentation     Sample test file for robocop-mcp tests


*** Test Cases ***
This is a test
    [Documentation]    This is a test case
    Log    Hello, World!
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
    assert isinstance(config.rules, list)
    assert config.violation_count == 20


def test_get_config_with_toml(tmp_path, monkeypatch):
    toml_file = tmp_path / "pyproject.toml"
    toml_file.write_text('[tool.robocop_mcp]\nDOC02 = "Missing documentation"\nviolation_count = 5\n')
    monkeypatch.setenv("ROBOCOPMCP_CONFIG_FILE", str(toml_file))
    config = get_config()
    assert config.robocopmcp_config_file == toml_file.resolve()
    assert config.violation_count == 5
    assert any(rule.rule_id == "DOC02" for rule in config.rules)


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
