<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/wait/wait02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/wait/wait02.c

Purpose: verifies `wait()` returns the pid and exit status of a terminated child.

Important APIs/types/functions: `verify_wait()` forks a child that exits with status 1, calls `wait(&status)`, checks returned pid, `WIFEXITED(status)`, and `WEXITSTATUS(status)`.

Control flow/state: one child exits immediately; the parent reaps exactly that child and inspects the wait status word.

Dependencies/integration: LTP `.forks_child = 1` and safe fork wrappers.

Risks/test signals: failures identify wrong child selection, broken status encoding, or wait errors. The explicit exit code makes the signal unambiguous.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/wait/wait02.c -->
