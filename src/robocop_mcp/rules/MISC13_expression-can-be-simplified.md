Simplify inline IF conditions or expressions where Robocop suggests simplification.
Typical cases: inline IF expressions that have redundant boolean comparisons
(for example `IF    ${var} == True` can be simplified to `IF    ${var}`). Fix
automatically by applying the simplest semantically-equivalent expression that
follows Robot Framework idioms (e.g., remove `== True`, remove redundant string
comparisons when truthiness suffices). Preserve behavior exactly and perform
minimal edits. Continue without asking.
