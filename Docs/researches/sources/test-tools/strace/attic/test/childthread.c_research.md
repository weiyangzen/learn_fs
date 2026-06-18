<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/attic/test/childthread.c -->
# sources/test-tools/strace/attic/test/childthread.c

Purpose: pthread/fork regression reproducer for strace tracking of a child process that exits while it still has a thread-child and the top-level parent later waits.

Important functions: `start0` pauses forever. `main` forks; the child creates a thread, sleeps to let it initialize, then exits with status 42. The parent sleeps, waits with `waitpid(-1, ...)`, asserts the expected child pid and exit status, prints `OK`, and exits.

Control flow: fork split with assertions enforcing scheduling assumptions. The thread remains paused when the process child exits.

State and persistence: no persistent state; process/thread lifecycle is the test state.

Dependencies and integration: requires pthreads, fork/wait semantics, and is intended to be run under `strace -f`.

Risks: timing uses `sleep(1)`/`sleep(2)` and can be flaky under extreme load. Assertions abort rather than producing structured TAP output. Test signals: under strace, output should include `OK` and correct child exit handling without stale attached-child accounting.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/attic/test/childthread.c -->
