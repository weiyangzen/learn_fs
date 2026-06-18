# sources/test-tools/liburing/test/pipe-bug.c

Purpose: regression test for task_work execution after pipe write/close/read sequencing, linked to a bug where task_work was gated incorrectly.

Important APIs/types/functions: `io_uring_prep_write`, `io_uring_prep_close`, `io_uring_prep_read`, `io_uring_wait_cqe_timeout`, pipe fds, `__kernel_timespec`, and `CHECK` macro.

Control flow: `pipe_bug()` creates a ring and pipe, writes "foobar" through io_uring, closes the write end through io_uring, reads available data, then reads EOF, each with a one-second timeout for close/read paths. `main()` repeats this 10,000 times.

State and persistence behavior: transient pipe and ring state only. `-ENOMEM` during ring creation is tolerated with a short sleep.

Dependencies and integration points: depends on pipe semantics and task_work completion paths in the kernel.

Risks and test signals: timeouts or failed CHECKs indicate close/read completions stuck behind task_work notification bugs. Repetition aims to expose intermittent failures.
