Fix automatically by renaming the file extension from `.robot` to `.resource` when
the file contains no Test Cases section and functions purely as a keywords
container. After renaming, update all `Resource` or `Import Resource` statements
referencing the old filename to point to the new `.resource` name. Only change the
file extension and corresponding import paths; do not alter tags, documentation,
keyword contents, variable sections, or ordering. Continue without asking.
