<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/answer.c -->
## sources/test-tools/strace/tests/answer.c

Purpose: Test program for injected or traced `exit_group` handling using a recognizable low-byte exit status.

Important APIs/types/functions: Calls raw `__NR_exit_group` and fallback `__NR_exit` with `kernel_ulong_t answer = 0xbadc0ded0000002aULL`.

Control flow: Invokes `exit_group(answer)` first; if that does not terminate, invokes `exit(answer)`, then returns 1 as an error path.

State and persistence: Terminates the process; no persistent state.

Dependencies and integration: Used by fault-injection/exit tests that expect the visible exit code to be 42 while preserving high-bit argument decoding.

Risks: Depends on syscall availability and process termination semantics. Normal execution never reaches clean `+++ exited` printing.

Test signals: Harness should observe exit status 42 or injected/fault behavior around `exit_group`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/answer.c -->
