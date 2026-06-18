# File Research: sources/os/plan9/9front/sys/src/cmd/upas/bayes/regcomp.h

This private header defines regexp compiler/executor constants and internal execution-list structs shared by the bayes regexp implementation.

Key contents:
- Defines `NSUBEXP` and `Resublist`, a fixed array of `Resub` match captures.
- Defines `Reinst.type` values: operands such as `RUNE`, `ANY`, `ANYNL`, `BOL`, `EOL`, `CCLASS`, `NCCLASS`, `END`, plus parser operators `START`, `LBRA`, `RBRA`, `OR`, `CAT`, `STAR`, `PLUS`, `QUEST`.
- Defines `Relist` and `Reljunk`, used by regexp execution routines outside this group for active NFA thread state.
- Declares internal helpers such as `_renewthread`, `_renewmatch`, and empty-thread variants.

Integration and risks:
- The numeric values encode both operator class and precedence, so changes must match compiler assumptions in `regcomp.c`.
- `LISTSIZE` and `BIGLISTSIZE` are fixed-size execution limits.
