import pytest

from .data import (
    TEST_1,
    TEST_NO_ERRORS,
    TEST_2,
    TEST_3_DUPLICATE_NAMES,
    TOML_FILE,
    ROBOCOP_TOML_FILE,
    TOML_FILE_RULE_AS_FILE,
    TOML_FILE_RULE_NAME_AS_FILE,
    TOML_FILE_RULE_NAME_ALL_AS_FILE,
)


@pytest.fixture
def test_1():
    return TEST_1


@pytest.fixture
def test_no_errors():
    return TEST_NO_ERRORS


@pytest.fixture
def test_2():
    return TEST_2


@pytest.fixture
def test_3_duplicate_names():
    return TEST_3_DUPLICATE_NAMES


@pytest.fixture
def toml_file_content():
    return TOML_FILE


@pytest.fixture
def robocop_toml_file_content():
    return ROBOCOP_TOML_FILE


@pytest.fixture
def toml_file_rule_as_file():
    return TOML_FILE_RULE_AS_FILE


@pytest.fixture
def toml_file_rule_name_as_file():
    return TOML_FILE_RULE_NAME_AS_FILE


@pytest.fixture
def toml_file_rule_name_all_as_file():
    return TOML_FILE_RULE_NAME_ALL_AS_FILE


@pytest.fixture
def toml_file_no_config():
    return """
[tool.other_tool]
foo = "bar"
"""


@pytest.fixture
def toml_file_no_robocop():
    return """
[tool.robocop_mcp]
violation_count = 5
rule_priority = ["DOC02"]

"""


@pytest.fixture
def toml_file_ignore():
    return """
[tool.robocop_mcp]
ignore = ["DOC02", "DOC03", "COM04"]
rule_priority = ["ARG01"]

"""
