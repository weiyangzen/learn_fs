# sources/test-tools/strace/src/sysent_shorthand_defs.h

Purpose: short macro definitions used to keep generated/manual syscall table rows compact.

Important APIs/types/functions: macros `TD`, `TF`, `TI`, `TN`, `TP`, `TS`, `TM`, `TST`, `TLST`, `TFST`, `TSTA`, `TSF`, `TFSF`, `TSFA`, `PU`, `NF`, `MA`, `SI`, `CST`, `TSD`, `TC`, `TCL`, `CC`, and test-only `SEN(a)`.

Control flow: when `STRACE_TESTS_H` is defined, macros collapse to zero/test placeholders; otherwise they expand to real `sysent.h` flags and `MAX_ARGS`. `SEN(a)` is defined elsewhere in production.

State and persistence behavior: preprocessor-only.

Dependencies and integration points: included before syscall table inclusion in `syscall.c` and paired with `sysent_shorthand_undefs.h`.

Risks: namespace pollution if not undefined; test and production expansion must stay compatible with table row syntax.

Test signals: table preprocessing in production and test builds, and verification that undef header removes all shorthand names.
