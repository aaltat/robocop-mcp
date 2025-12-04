import pytest
from approvaltests import verify

from src.robocop_mcp.server import (
    get_robocop_report,
)


@pytest.mark.asyncio
async def test_get_robocop_report_basic_functionality(tmp_path, monkeypatch, test_1, toml_file_content):
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
async def test_get_robocop_report_with_custom_rule_from_file(
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
async def test_get_robocop_report_with_rule_name_mapped_to_file(
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
async def test_get_robocop_report_applies_rule_priority_ordering(
    tmp_path, monkeypatch, test_1, toml_file_content
):
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
async def test_get_robocop_report_priority_using_rule_names(
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
async def test_get_robocop_report_priority_by_name_with_rule_id_fix(
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
async def test_get_robocop_report_handles_invalid_priority_rule(
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
async def test_get_robocop_report_returns_empty_when_no_violations(
    tmp_path, monkeypatch, test_no_errors, toml_file_content
):
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
async def test_get_robocop_report_with_missing_robocop_mcp_config(
    tmp_path, monkeypatch, test_1, toml_file_no_config
):
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
async def test_get_robocop_report_with_nonexistent_config_file(tmp_path, monkeypatch, test_1):
    toml_file = tmp_path / "nothere.toml"
    monkeypatch.setenv("ROBOCOPMCP_CONFIG_FILE", str(toml_file))
    robot_file = tmp_path / "sample.robot"
    robot_file.write_text(test_1)
    result = await get_robocop_report(str(robot_file))
    lines = [line for line in result.splitlines() if not line.startswith("file")]
    lines_filtered = "\n".join(lines)
    verify(lines_filtered)


@pytest.mark.asyncio
async def test_get_robocop_report_without_robocop_mcp_section(
    tmp_path, monkeypatch, test_1, toml_file_no_robocop
):
    toml_file = tmp_path / "pyproject.toml"
    toml_file.write_text(toml_file_no_robocop)
    monkeypatch.setenv("ROBOCOPMCP_CONFIG_FILE", str(toml_file))
    robot_file = tmp_path / "sample.robot"
    robot_file.write_text(test_1)
    result = await get_robocop_report(str(robot_file))
    assert "file: " in result
    assert "sample.robot" in result


@pytest.mark.asyncio
async def test_get_robocop_report_handles_malformed_config_values(
    tmp_path, monkeypatch, test_1, toml_file_no_robocop
):
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
async def test_get_robocop_report_respects_ignore_rules_by_id(
    tmp_path, monkeypatch, test_1, toml_file_ignore
):
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
async def test_get_robocop_report_respects_ignore_rules_by_name(
    tmp_path, monkeypatch, test_1, toml_file_ignore
):
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
async def test_get_robocop_report_with_separate_robocop_config_file(
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
async def test_get_robocop_report_with_only_robocop_config_file(
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
