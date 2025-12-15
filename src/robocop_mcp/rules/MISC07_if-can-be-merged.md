Merge consecutive IF statements that test the same condition into a single IF
block. This typically appears when an inline IF or a subsequent IF repeats the
same condition as a previous IF. Fix automatically by combining the actions into
one IF/END block in the original order. Make the smallest possible edit: remove
the redundant IF line(s) and place the action(s) inside the existing IF block,
preserving indentation and surrounding context. Do not change documentation, tags,
variable names, or other unrelated code. Continue without asking.
