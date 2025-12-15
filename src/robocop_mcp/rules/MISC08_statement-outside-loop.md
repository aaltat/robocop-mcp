Loop control statements are used outside of a loop (FOR or WHILE) where they're
not valid. These statements should only be used inside loops:
- `CONTINUE` / `Continue For Loop` / `Continue For Loop If`
- `BREAK` / `Exit For Loop` / `Exit For Loop If`

This is a syntax/logic error. Review the code structure - the loop control
statement needs to be moved inside a FOR or WHILE block, or removed if it's
not needed.
