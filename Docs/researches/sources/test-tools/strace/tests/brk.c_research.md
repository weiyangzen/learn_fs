<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/brk.c -->
## sources/test-tools/strace/tests/brk.c

Purpose: Minimal decoder test for the `brk` syscall with NULL argument.

Important APIs/types/functions: Calls `syscall(__NR_brk, NULL)` and prints the returned program break as hex.

Control flow: Invokes `brk(NULL)`, prints an escaped regex-style expected line `brk\(NULL\) = %#lx`, then exits without the usual `+++ exited` marker.

State and persistence: Reads current program break without changing it.

Dependencies and integration: Uses `tests.h`, `scno.h`, and raw syscall invocation; included in decoder tests.

Risks: Output intentionally resembles a regex expectation and omits the standard exit marker, so harness expectations must account for that.

Test signals: Expected output is a single `brk(NULL)` line with the current break address.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/brk.c -->
