# sources/test-tools/ltp/testcases/kernel/fs/fs_fill/fs_fill.c

Purpose: multi-threaded filesystem fill stress test that repeatedly drives mounted filesystems to `ENOSPC` while unlinking one file per worker loop to keep pressure cycling.

Important APIs/types/functions: LTP `struct tst_test`, `tst_fill_fs`, `enum tst_fill_access_pattern`, `SAFE_PTHREAD_CREATE`, `SAFE_PTHREAD_JOIN`, `SAFE_OPENDIR`, `SAFE_READDIR`, `SAFE_UNLINK`, `tst_atomic_t`, `worker`, `testrun`, `setup`, and `cleanup`.

Control flow: setup allocates `ncpus + 2` workers and per-thread directories below `mntpoint/subdir`. Each test iteration starts all worker threads with access pattern index `n`, waits until at least one `ENOSPC` after one second or more than 100 `ENOSPC` events, stops threads, joins them, and reports runtime. Workers fill their directory, increment the ENOSPC counter, then unlink one entry before looping.

State/persistence behavior: creates and deletes files on a mounted test filesystem. `workers`, `run`, and `enospc_cnt` are process state; filesystem state is discarded with the LTP mounted-device cleanup.

Dependencies/integration: requires root, a mountable device of at least 1024 MiB, all-filesystems iteration, pthreads, and LTP safe wrappers. The Makefile adds `-pthread`.

Risks/test signals: timing-based termination can vary by filesystem speed. Directory cleanup removes only one file per loop, so very large file counts can accumulate briefly. Success is a `TPASS` with observed `ENOSPC`; hangs are limited by the 300-second timeout.
