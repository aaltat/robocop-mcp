TEST_1 = """
*** Test Cases ***
this is a test
    Log    Hello, World!"""


TOML_FILE = """
[tool.robocop]
language = ["en"]
[tool.robocop_mcp]
DOC02 = "Missing documentation"
violation_count = 5
"""

ROBOCOP_TOML_FILE = """
[lint]
ignore = ["DOC02", "DOC03", "COM04", "COM04"]
"""

TOML_FILE_RULE_AS_FILE = """
[tool.robocop_mcp]
DOC02 = REPLACE_ME
violation_count = 5
rule_priority = ["DOC02"]

[tool.robocop]
language = ["en"]

"""

TOML_FILE_RULE_NAME_AS_FILE = """
[tool.robocop_mcp]
missing-doc-test-case = REPLACE_ME
violation_count = 5
rule_priority = ["DOC02"]

[tool.robocop]
language = ["en"]

"""

TOML_FILE_RULE_NAME_ALL_AS_FILE = """
[tool.robocop_mcp]
missing-doc-test-case = REPLACE_ME
violation_count = 5
rule_priority = ["missing-doc-test-case"]

[tool.robocop]
language = ["en"]

"""

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

TEST_3_DUPLICATE_NAMES = """\
*** Test Cases ***
Example Test
    Log    Hello, World!
Example Test
    Log    Hello, World!

"""
