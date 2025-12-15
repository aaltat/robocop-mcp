Fix automatically by converting inline IF-ELSE statements that were incorrectly
split into proper multiline IF-ELSE-END blocks. The pattern is usually a broken
inline IF that needs to become:
```
IF    condition
    keyword
ELSE
    keyword
END
```
Continue without asking.
