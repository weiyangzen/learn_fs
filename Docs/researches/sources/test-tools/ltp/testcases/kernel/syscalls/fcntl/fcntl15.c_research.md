# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl15.c

Purpose: checks POSIX file-lock lifetime rules when descriptors are closed, comparing duplicated fds, independently opened fds in the same process, and locks held by another process.

Important APIs/types/functions: `fcntl(F_SETLK)`, `fcntl(F_DUPFD)`, `SAFE_OPEN`, `SAFE_FORK`, `TST_CHECKPOINT_*`, `struct flock`, and predefined `lock_one`/`lock_two`.

Control flow: for each case, parent opens and locks region one, obtains region-two lock either by dup, separate open, or child process, then forks a tester. The tester first verifies both regions are locked, waits while parent closes `fd[0]`, then verifies same-process locks disappeared for dup/open cases while child-held region-two lock remains in the fork case.

State/persistence behavior: creates one file, writes data, holds locks through fd duplication/opening/forking, and uses checkpoints for synchronization. Closing a descriptor is the state transition under test.

Dependencies/integration: modern LTP with fork and checkpoint support.

Risks/test signals: POSIX locks are per-process, not per-fd, so expected behavior differs from open-file-description locks. Failures indicate lock lifetime semantics changed or synchronization failed.
