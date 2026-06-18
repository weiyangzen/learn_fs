# sources/test-tools/strace/src/sysent_shorthand_undefs.h

Purpose: removes syscall table shorthand macros after table inclusion.

Important APIs/types/functions: `#undef` list for every shorthand macro from `sysent_shorthand_defs.h`, including `SEN`.

Control flow: no runtime flow; preprocessor cleanup.

State and persistence behavior: prevents macro definitions from persisting into later code.

Dependencies and integration points: included immediately after generated syscall tables in `syscall.c`.

Risks: missing an undef can silently affect later identifiers; undefining a macro that was not defined is safe.

Test signals: preprocess `syscall.c` and ensure no shorthand macro remains available after inclusion.
