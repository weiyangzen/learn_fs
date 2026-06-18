# sources/test-tools/liburing/test/sqpoll-exec.c

Purpose: regression for SQPOLL close task_work ordering where a file closed via io_uring must be immediately closed by the time its close CQE is received, allowing subsequent exec.

Important APIs/types/functions: `IORING_SETUP_SQPOLL`, `io_uring_prep_openat`, `io_uring_prep_close`, `execve`, fork/wait, `stat`, and helper `t_create_ring_params`.

Control flow: finds `exec-target.t` in current or `test/`, opens it through an SQPOLL ring, closes the returned fd through io_uring, waits for the close CQE, forks, and the child execs the target. `main()` repeats this sequence 20 times.

State/persistence behavior: uses the executable file as a target and mutates only fd lifetime. No file contents are changed.

Dependencies/integration: depends on SQPOLL support and presence of `exec-target.t`. Missing target or SQPOLL support skips.

Risks/test signals: if close task_work is delayed, `execve` can fail because the executable is still open for write. Failures are child nonzero exit, open/close CQE errors, or target lookup failure.
