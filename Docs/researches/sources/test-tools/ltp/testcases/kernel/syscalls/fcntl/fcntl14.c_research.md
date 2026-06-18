# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl14.c

Purpose: randomized two-process record-lock test that checks whether child locks block exactly when their byte ranges conflict with parent locks, across normal and mandatory-locking variants.

Important APIs/types/functions: `fcntl(F_SETLK)`, `fcntl(F_GETLK)`, `struct flock`, `SAFE_FORK`, shared `mmap` results, `lseek`, `rand`, `tst_parse_int`, and option `-n` controlling operation count.

Control flow: setup writes a small file, optionally enables mandatory locking in variant 1, and maps shared results. Each generated testcase chooses a file position and random parent/child ranges using `SEEK_CUR`, computes overlap and blocking expectation, parent places its lock, child queries with `F_GETLK`, verifies conflict metadata or `F_UNLCK`, then tries `F_SETLK` expecting either `EWOULDBLOCK` or success.

State/persistence behavior: each iteration opens the same file, sets process locks, forks a child observer, and closes the fd to clear locks. Shared anonymous mapping reports child assertion state.

Dependencies/integration: modern LTP, tempdir, fork, optional mandatory locking support, and skips NFS.

Risks/test signals: randomized coverage can be non-reproducible because it seeds with `time(0)`. Failing debug output includes generated ranges and expected blocking mode.
