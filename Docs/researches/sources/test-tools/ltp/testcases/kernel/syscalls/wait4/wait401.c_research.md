<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/wait4/wait401.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/wait4/wait401.c

Purpose: verifies `wait4(pid, &status, 0, &rusage)` waits for a specific child and reports normal zero exit status.

Important APIs/types/functions: child waits until parent is sleeping via `TST_PROCESS_STATE_WAIT(getppid(), 'S', 0)` then exits. Parent calls `wait4()`, checks pid, `WIFEXITED`, and `WEXITSTATUS == 0`; `struct rusage` is supplied but not inspected.

Control flow/state: the child synchronization increases confidence the parent actually blocks in `wait4()`. State is only process lifecycle and returned status.

Dependencies/integration: uses BSD `wait4` interface, LTP fork metadata, and process state polling.

Risks/test signals: status and pid mismatches are direct. The rusage pointer path is covered for ABI validity, but resource contents are not validated.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/wait4/wait401.c -->
