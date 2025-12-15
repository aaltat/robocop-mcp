Fix automatically by ensuring each continuation line after `[Arguments]` contains
at most one argument assignment. Split lines with multiple arguments into separate
continuation lines starting with `...` preserving order and spacing of tokens.
Do not modify argument names, default values, tags, documentation, or add/remove
other lines. Only split the flagged lines. Continue without asking.
