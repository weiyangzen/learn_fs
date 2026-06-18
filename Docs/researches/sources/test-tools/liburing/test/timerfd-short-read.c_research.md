# sources/test-tools/liburing/test/timerfd-short-read.c

Purpose: regression test that io_uring read handling on anonymous-inode descriptors such as timerfd supports short reads correctly. It guards against kernel behavior that treated anonymous inodes like regular files and broke short read/write handling.

Important APIs/types/functions: `sig_alrm`, `timerfd_create`, `timerfd_settime`, `io_uring_queue_init_params`, `io_uring_prep_read`, `io_uring_submit`, `io_uring_wait_cqe`, `alarm`, and `SIGALRM`.

Control flow: main creates an io_uring and a monotonic timerfd. It submits a read for two `unsigned long` values, arms the timer to expire after 10 ms, installs a one-second alarm fail-safe, then waits for a CQE. The test succeeds if the wait returns instead of hanging; it does not require a specific byte count.

State/persistence behavior: no persistent state. The timerfd counter state is consumed by the pending read and closed afterward.

Dependencies/integration: depends on Linux timerfd, signal handling, io_uring read operations, and anonymous-inode file operations.

Risks/test signals: primary signal is non-hang. A hang triggers `sig_alrm` and `T_EXIT_FAIL`; setup failures or wait errors also fail.
