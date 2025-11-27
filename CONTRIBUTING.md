# Custom rule fixes

By default robocop-mcp will suggest fixes based on the robocop rule documentation,
but for some cases those fixes are not suitable for LLM to create a good fix.

If you have an idea how to instruct LLM to apply an fix for specific rule,
create a markdown file in `src/robocop_mcp/rules` folder with the rule id
as the name. Example for `DUP01` rule id, file name should be `DUP01.md`.

Write the instruction in the file and create a PR to the repository.
instructions to create PR can be found from GitHub
[documentation](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request)
