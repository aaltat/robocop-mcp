# Contributing

Project uses [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/)
which allows create releases and releases notes automatically based on the
commit massages. This to work, we need you to start your commit messages
as explained
[summary documentation](https://www.conventionalcommits.org/en/v1.0.0/#summary)
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

This project does not use the `scope` and if you are unsure, your first line in
the commit message must start:
```
fix: explain why change is made
```
One PR can contain several commit messages, but all commit messages must be
formatted according the
[conventional commits](https://www.conventionalcommits.org/en/v1.0.0/)
rules.

# Custom rule fixes

By default robocop-mcp will suggest fixes based on the robocop rule documentation,
but for some cases those fixes are not suitable for LLM to create a good fix.

If you have an idea how to instruct LLM to apply an fix for specific rule,
create a markdown file in `src/robocop_mcp/rules` folder with the rule id
as the name. Example for `DUP01` rule id, file name should be `DUP01.md`.

Write the instruction in the file and create a PR to the repository.
instructions to create PR can be found from GitHub
[documentation](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request)
