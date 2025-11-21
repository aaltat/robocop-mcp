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
