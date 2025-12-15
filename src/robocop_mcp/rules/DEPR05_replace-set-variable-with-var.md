Replace `Set Variable`/`Set <scope> Variable` with `VAR` syntax.

VAR    ${local}     local value            # replaces Set Variable
VAR    ${TEST}      test value            scope=TEST    # replaces Set Test Variable
VAR    ${SUITE}     suite value           scope=SUITE   # replaces Set Suite Variable
VAR    ${GLOBAL}    global value          scope=GLOBAL  # replaces Set Global Variable
