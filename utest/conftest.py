import pytest



@pytest.fixture
def test_1():
    return """
*** Test Cases ***
this is a test
    Log    Hello, World!"""


@pytest.fixture
def test_no_errors():
    return """\
*** Settings ***
Documentation     Sample test file for robocop-mcp tests


*** Test Cases ***
This is a test
    [Documentation]    This is a test case
    Log    Hello, World!
"""


@pytest.fixture
def test_2():
    return """
*** Test Cases ***
Example Test 1
    Log    Hello, World!
Example Test 2
    Log    Hello, World!"""


@pytest.fixture
def test_3_duplicate_names():
    return """\
*** Test Cases ***
Example Test
    Log    Hello, World!
Example Test
    Log    Hello, World!

"""


@pytest.fixture
def toml_file_content():
    return """
[tool.robocop]
language = ["en"]
[tool.robocop_mcp]
DOC02 = "Missing documentation"
violation_count = 5
reruns = 2
"""


@pytest.fixture
def robocop_toml_file_content():
    return """
[lint]
ignore = ["DOC02", "DOC03", "COM04", "COM04"]
"""


@pytest.fixture
def toml_file_rule_as_file():
    return """
[tool.robocop_mcp]
DOC02 = REPLACE_ME
violation_count = 5
rule_priority = ["DOC02"]

[tool.robocop]
language = ["en"]

"""


@pytest.fixture
def toml_file_rule_name_as_file():
    return """
[tool.robocop_mcp]
missing-doc-test-case = REPLACE_ME
violation_count = 5
rule_priority = ["DOC02"]

[tool.robocop]
language = ["en"]

"""


@pytest.fixture
def toml_file_rule_name_all_as_file():
    return """
[tool.robocop_mcp]
missing-doc-test-case = REPLACE_ME
violation_count = 5
rule_priority = ["missing-doc-test-case"]

[tool.robocop]
language = ["en"]

"""


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
