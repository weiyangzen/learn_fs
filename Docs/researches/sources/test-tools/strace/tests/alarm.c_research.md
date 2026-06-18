<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/alarm.c -->
## sources/test-tools/strace/tests/alarm.c

Purpose: Simple decoder test for `alarm` argument truncation/printing.

Important APIs/types/functions: Calls `syscall(__NR_alarm, arg)` with a 64-bit-looking value whose low 32 bits are 42, and prints `sprintrc`.

Control flow: Guarded by `__NR_alarm`; if available, invokes alarm once and prints expected `alarm(42)` representation; otherwise emits skip main.

State and persistence: Arms a process alarm but exits immediately, leaving no external state.

Dependencies and integration: Uses `tests.h`, `scno.h`, and generic result formatting.

Risks: The active alarm could theoretically interfere if execution were delayed, but the test exits right away. Architectures without `alarm` skip.

Test signals: Output should show the normalized unsigned argument `42` and clean exit.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/alarm.c -->
