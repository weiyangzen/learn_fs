<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid03.c

Purpose: verifies waiting for a specific child pid succeeds once and then fails with `ECHILD` after that child has been reaped.

Important APIs/types/functions: `MAX_CHILDREN` is 25. `run()` forks all children, selects the midpoint pid, and calls `check_waitpid(pid, reaped)` twice. `check_waitpid()` validates either returned pid or `-1/ECHILD` depending on expected reaped state.

Control flow/state: many children exit immediately; parent reaps one chosen child explicitly, then proves repeated wait on the same pid fails. `tst_reap_children()` cleans the rest.

Dependencies/integration: LTP fork metadata handles child cleanup. No checkpoints are needed because children exit immediately.

Risks/test signals: a wrong pid return, non-`ECHILD` errno, or repeated successful reap indicates waitpid bookkeeping regression.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid03.c -->
