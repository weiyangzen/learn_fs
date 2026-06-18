# sources/test-tools/liburing/test/sq-poll-kthread.c

Purpose: verifies SQPOLL kernel threads stop after a userspace process exits, both when the process explicitly closes the ring and when it does not.

Important APIs/types/functions: `IORING_SETUP_SQPOLL`, `sq_thread_idle`, fixed-file registration, `io_uring_prep_writev`, fork/wait, `system("ps --ppid 2 | grep io_uring-sq")`, and pipe I/O.

Control flow: child process creates an SQPOLL ring, registers pipe write end, submits a fixed-file writev, waits for successful CQE, and optionally calls `io_uring_queue_exit`. Parent waits for child, sleeps briefly, and scans kernel threads for lingering `io_uring-sq`. `main()` runs both explicit-exit and no-exit variants.

State/persistence behavior: state is SQPOLL kthread lifetime, pipe fds, and child process exit. No files persist.

Dependencies/integration: depends on process/kthread visibility through `ps`, SQPOLL permissions, and fixed-file write support.

Risks/test signals: lingering SQPOLL thread after child exit is failure. The `ps|grep` heuristic can be environment-sensitive if unrelated io_uring SQ threads exist.
