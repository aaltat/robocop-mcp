A disabler directive (`# robocop:off=<rule>`) is present but the violation it's
supposed to disable doesn't exist at that location.

Fix automatically by removing the unused disabler comment. Continue without
asking.
