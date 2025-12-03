# Robocop MCP server
Robocop MCP server helps users to resolve their static code analysis
errors and warnings with help of an LLM. It has two tools to help
resolve Robocop rules:

## Get robocop report
Get robocop report tool allows calls `robocop check` command and
returns one rule violation (maximum 20 from one rule) to LLM.
The rule violation summary also contains default recommendation
how the rule violation can be fixed. User than can accept the
suggested proposal or tell LLM a different way to fix the rule
violation.

The maximum number of rule violations, proposed fix for a rule
and many more things can be configured in the `pyproject.toml`
file. See [Configuration](#configuration) chapter for more details.

## Run robocop format
You can also run robocop format tool. Because robocop has complex
commandline syntax, robocop-mcp only support giving file or folder
as an argument for the `format` command. Rest of the configuration
should be placed in the
[robocop configuration file](https://robocop.dev/stable/configuration/).
The `--reruns` option is set to 10.

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
```
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

And example if user wants to prioritize the `ARG01` and `ARG02` to be fixed first, then
`rule_priority` would look like this.

```toml
[tool.robocop_mcp]
rule_priority = [
    "ARG01",
    "ARG02"
]
```

It is also possible to define rule priority by rule name. Example if there is a need to
define `ARG01` and `ARG02` rules by name, then `rule_priority` would look like:
```toml
[tool.robocop_mcp]
rule_priority = [
    "unused-argument",
    "argument-overwritten-before-usage"
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
```toml
[tool.robocop_mcp]
ARG01 = "my_rules/ARG01.md"
```

It is also possible to define custom fix proposals by rule name.
Example to provide custom fix proposal for `ARG01` by name, then
toml file would look like:
```toml
[tool.robocop_mcp]
unused-argument = "my_rules/unused-argument.md"

```
## Ignore rules
The recommended way to ignore rules is to ignore rules in the
robocop tools section in the `pyproject.toml`. In that case
rules are ignored by Robocop and ignored rules are not visible for the
robocop-mcp serve either.

If there is need to ignore rules only for robocop-mcp, then add
`ignore` (list) setting to the `pyproject.toml` file. Example if there is a
need to ignore `DOC02`, `DOC03` and `COM04` rules, then `pyproject.toml`
should have:

```toml
[tool.robocop_mcp]
ignore = ["DOC02", "DOC03", "COM04"]
```
It is also possible to to ignore rules by rule name. If same rules
as in above would need to ignored, then ignore list would look like:

```toml
[tool.robocop_mcp]
ignore = [
    'missing-doc-test-case',
    'missing-doc-suite',
    'ignored-data'
]
```

## Support separate robocop configuration file
Although robocop-mcp only supports `pyproject.toml`, the robocop itself
does support multiple different configuration files. If your robocop
configuration is not in `pyproject.toml`, then the separate configuration
file can be defined in `ROBOCOPMCP_ROBOCOP_CONFIG_FILE` environment
variable. Example `mcp.json`:

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
            "env": {
                "ROBOCOPMCP_CONFIG_FILE": "${workspaceFolder}/pyproject.toml",
                "ROBOCOPMCP_ROBOCOP_CONFIG_FILE": "${workspaceFolder}/robocop.toml",
            }
        }
    }
}
```

## Robocop reruns

It is possible to configure how `robocop format --reruns` command line argument
is set. This is controlled in the `pyproject.toml` file by `reruns` (int) setting.
By default value is set to ten, but the set it to two add the following to
`pyproject.toml` file:
```toml
[tool.robocop]
reruns = 2
```

# Contributing fix instructions for rule

Users can contribute their instructions to for rule fixes in the repository. This
is explained in the
[CONTRIBUTING.md](https://github.com/aaltat/robocop-mcp/blob/main/CONTRIBUTING.md)
file. If there is not fix, either from robocop-mcp or by user defined fixes, then
`robocop` documentation is used as fix instruction to LLM. User can always write
their own fix explanation in the prompt, but if that is not one off, then it is
easier to define user defined rule fix in a file or contribute a fix to the
robocop-mcp project.
