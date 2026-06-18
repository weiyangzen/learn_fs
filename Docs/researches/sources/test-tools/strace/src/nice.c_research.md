<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/nice.c -->
# sources/test-tools/strace/src/nice.c

Purpose: syscall decoder for `nice`.

Important APIs/types/functions: `SYS_FUNC(nice)`.

Control flow: prints the single signed `increment` argument and marks the syscall decoded.

State and persistence behavior: no state.

Dependencies and integration points: integrated through strace syscall table and generic argument printing helpers from `defs.h`.

Risks: low; only sign formatting matters.

Test signals: trace positive, zero, and negative nice increments.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/nice.c -->
