# Robocop MCP server
Robocop MCP server helps users to resolve their static code analysis
errors and warnings with help of an LLM.

# Install

Install with pip:
`pip install robocop-mcp`

# Running robocop-mcp server

For running MCP server in VS Code workspace:

1. Create a .vscode/mcp.json file in your workspace.
2. Add following configuration to the mcp.json file:
```json
{
    "servers": {
        "robocop-mcp":{
            "type": "stdio",
            "command": "uv",
            "args": [
                "run",
                "src/robocop_mcp",
            ],
            "env": {
                "ROBOCOPMCP_CONFIG_FILE": "${workspaceFolder}/pyproject.toml"
            }
        }
    }
}
````
3. Remember to click start button in the `mcp.json` file

For general detail about configuring MCP server in VS Code,
see the VS Code
[documentation](https://code.visualstudio.com/docs/copilot/customization/mcp-servers#_configuration-format)
