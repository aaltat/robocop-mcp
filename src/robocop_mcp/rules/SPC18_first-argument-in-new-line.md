Place the first argument on the same line as the `[Arguments]` setting instead of
on a new line. If there are multiple arguments and they don't fit, keep the first
argument on the same line as `[Arguments]` and move the remaining arguments to
continuation lines.

Example - Before:
```robot
[Arguments]
...    ${first_arg}
---    ${second_arg}
```

After:
```robot
[Arguments]    ${first_arg}
...    ${second_arg}
```
