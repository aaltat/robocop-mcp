Suggest in text how to split or shorten the keyword. Only if the keyword contains
a list of many similar things, such as setting 30 variables,
add `# robocop:off=too-many-calls-in-keyword` comment with comment explaining why.
If splitting, try to come up with groupings that make sense, if the keyword is
sequential. If it contains a loop, consider splitting out the part inside the loop
to a separate keyword. Chose splits that give clear and helpful namings.
