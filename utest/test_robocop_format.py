from unittest.mock import patch

import pytest
from approvaltests.approvals import verify

from src.robocop_mcp.server import run_robocop_format
from .data import TEST_1, TOML_FILE, ROBOCOP_TOML_FILE, TOML_FILE_RULE_AS_FILE


@pytest.mark.asyncio
async def test_run_robocop_format_with_path(tmp_path):
    robot_file = tmp_path / "sample.robot"
    robot_file.write_text(TEST_1)
    result = await run_robocop_format(robot_file)
    assert "sample.robot" in result
    lines = [line for line in result.splitlines() if not line.startswith("Reformatted ")]
    lines_filtered = "\n".join(lines)
    verify(lines_filtered)


@pytest.mark.asyncio
async def test_run_robocop_format_with_robocop_config_file(tmp_path, monkeypatch):
    toml_file = tmp_path / "pyproject.toml"
    toml_file.write_text(TOML_FILE)
    monkeypatch.setenv("ROBOCOPMCP_CONFIG_FILE", str(toml_file))
    robocop_toml_file = tmp_path / "robocop.toml"
    robocop_toml_file.write_text(ROBOCOP_TOML_FILE)
    monkeypatch.setenv("ROBOCOPMCP_ROBOCOP_CONFIG_FILE", str(robocop_toml_file))
    robot_file = tmp_path / "sample.robot"
    robot_file.write_text(TEST_1)

    with patch("src.robocop_mcp.mcp_format.format_files") as mock_format_files:
        mock_format_files.return_value = None
        result = await run_robocop_format(robot_file)

        # Assert format_files was called with correct arguments
        mock_format_files.assert_called_once()
        mock_format_files.assert_called_once_with(sources=[robot_file], configuration_file=robocop_toml_file)
        assert "sample.robot" in result or result is not None


@pytest.mark.asyncio
async def test_run_robocop_format_with_pyproject_file(tmp_path, monkeypatch):
    toml_file = tmp_path / "pyproject.toml"
    text = TOML_FILE_RULE_AS_FILE.replace("REPLACE_ME", '"Missing documentation"')
    toml_file.write_text(text)
    monkeypatch.setenv("ROBOCOPMCP_CONFIG_FILE", str(toml_file))
    robot_file = tmp_path / "sample.robot"
    robot_file.write_text(TEST_1)

    with patch("src.robocop_mcp.mcp_format.format_files") as mock_format_files:
        mock_format_files.return_value = None
        result = await run_robocop_format(robot_file)

        # Assert format_files was called with correct arguments
        mock_format_files.assert_called_once_with(sources=[robot_file], configuration_file=toml_file)
        assert "sample.robot" in result or result is not None


@pytest.mark.asyncio
async def test_run_robocop_format_with_exception(tmp_path):
    """Test that run_robocop_format handles exceptions from format_files."""
    robot_file = tmp_path / "sample.robot"
    robot_file.write_text(TEST_1)

    with patch("src.robocop_mcp.mcp_format.format_files") as mock_format_files:
        mock_format_files.side_effect = Exception("Format error occurred")

        result = await run_robocop_format(robot_file)
        mock_format_files.assert_called_once_with(sources=[robot_file])
        verify(result)
