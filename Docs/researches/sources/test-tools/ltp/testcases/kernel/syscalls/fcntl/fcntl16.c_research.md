# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl16.c

Purpose: legacy blocking-lock wakeup test. It verifies children waiting on lock boundaries are notified or remain blocked as expected when the parent changes overlapping locks, across normal, mandatory, and mandatory plus `O_NDELAY` modes.

Important APIs/types/functions: `fcntl(F_SETLK)`, `fcntl(F_SETLKW)`, `struct flock`, signal handlers for `SIGUSR1`, `SIGUSR2`, `SIGALRM`, child process management, `testcases[]` describing parent/child lock sequences, and constants `NOBLOCK`, `WILLBLOCK`, `IGNORED`.

Control flow: each `run_test()` case opens a file, writes data, sets one or two parent locks, forks up to two children that attempt blocking locks, waits for readiness signals, applies parent lock changes, then waits for child exits. Children expected to remain blocked are interrupted by signal and should exit with status 1; nonblocking-success children exit 0.

State/persistence behavior: repeatedly creates locks on one temp file and uses signals plus child exit codes as synchronization state. The file is reopened for each testcase and unlinked after the run.

Dependencies/integration: legacy LTP harness, mandatory locking support, NFS detection, signals, alarms, and fork.

Risks/test signals: timing-sensitive and legacy mandatory locking behavior may be disabled on modern systems. Failures include children not signaling, unexpected child status, lock setup failure, or timeout.
