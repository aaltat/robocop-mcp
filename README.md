# Robocop MCP server
Robocop MCP server helps users to resolve their static code analysis
errors and warnings with help of an LLM.

# Install

Install with pip:
`pip install robocop-mcp`

# Running robocop-mcp server

## running MCP server in VS Code workspace:

1. Create a `.vscode/mcp.json` file in your workspace.
2. Add following configuration to the mcp.json file:
```json
{
    "servers": {
        "robocop-mcp":{
            "type": "stdio",
            "command": "${workspaceFolder}/.venv/bin/python",
            "args": [
                "-m",
                "robocop_mcp",
            ],

        }
    }
}
````
3. Change your CopPilot chat to Agent mode and select
suitable model for your use.
4. Remember to click start button in the `mcp.json` file

For general detail about configuring MCP server in VS Code,
see the VS Code
[documentation](https://code.visualstudio.com/docs/copilot/customization/mcp-servers#_configuration-format)

# Using robocop-mcp

https://github.com/user-attachments/assets/f446f31f-a91e-4cc1-bae0-6b691469dfba

# Configuration

The robocop-mcp server can configured by using
[pyproject.toml](https://packaging.python.org/en/latest/specifications/pyproject-toml/)
file. The robocop-mcp server uses `[tool.robocop_mcp]` section in the toml file.

To robocop-mcp server see the the toml file, a ROBOCOPMCP_CONFIG_FILE environment
variable must be set. Example in the `mcp.json` file:
```json
{
    "servers": {
        "robocop-mcp":{
            "type": "stdio",
            "command": "python",
            "args": [
                "-m",
                "robocop_mcp",
            ],
            "env": {"ROBOCOPMCP_CONFIG_FILE": "${workspaceFolder}/pyproject.toml"},
        }
    }
}
```

## Priority of Robocop rules
Some rules are more important to fix than others or perhaps you want to use
certain type of LLM to solve certain type of rule violations. In this case
you can use `rule_priority` (list) to define which rule are first selected by the
robocop-mcp and given to the LLM model. The `rule_priority` is a list of
robocop rule id's. You can list all the rules with command:
```shell
> robocop list rules
````
And if one one rules looks like this:
```shell
Rule - ARG01 [W]: unused-argument: Keyword argument '{name}' is not used (enabled)
```
Then rule id is the `ARG01`.

And example if user wants to prioritize the `ARG01` and `ARG02` to be fixed first, then `rule_priority` would look like this.

```toml
[tool.robocop_mcp]
rule_priority = [
    "ARG01",
    "ARG02"
]
```

If `rule_priority` is not defined, robocop-mcp will select take first rule
returned by `robocop` and use it to find similar rule violations. If no
rules match to `rule_priority` list, first rule returned by Robocop is used.

## Maximum amount violations returned
To not to clutter the LLM context with all the rule violations found from
the test data, by default robocop-mcp will return twenty (20) violations
from robocop. This can be changed by defining different value in the
`violation_count` (int) setting.

To make robocop-mcp return 30 rule violations:
```toml
[tool.robocop_mcp]
violation_count = 30
```

How many rule violations the robocop-mcp should return depends on the
LLM model being used, how verbose the proposed fix is and how long the
LLM model context have been in use. It is hard to give good guidance on
this subject, because LLM models change at fast pace and there are some
many different models available.

## Custom fix proposals
Each rule violation contains robocop default rule documentation how
the problem can be addressed. In some cases, this may lead to LLM to wrong
solution or you want to apply custom way to fix the specific rule.
Custom solution can be defined in text file (markdown is recommended,
because it is easy for LLM to understand.) and defining custom rule
files in the `pyproject.toml`. Each rule where custom fix is defined
is defined as key in toml file and value must point to a text file.

Example if there need to define custom fix for `ARG01`, create
`ARG01.md` file, example in a `my_rules` folder. Then `pyproject.toml`
should have:
```json
[tool.robocop_mcp]
ARG01 = "my_rules/ARG01.md"
```
