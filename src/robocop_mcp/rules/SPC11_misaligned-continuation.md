Continuation marker (`...`) must be aligned with the starting row. The `...` should
have the same indentation as the first line of the multi-line statement.

Example - Before:
```robot
Keyword Name
  ...    arg1
```

After:
```robot
Keyword Name
...    arg1
```

Fix automatically by aligning continuation markers. Continue without asking.
