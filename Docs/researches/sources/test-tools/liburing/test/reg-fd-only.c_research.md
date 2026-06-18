# sources/test-tools/liburing/test/reg-fd-only.c

Purpose: tests rings created with `IORING_SETUP_REGISTERED_FD_ONLY | IORING_SETUP_NO_MMAP`. It verifies that already-registered ring fds behave correctly, that closing the ring fd still permits register operations through the registered-ring path, and that the ring remains usable for NOP submissions.

Important APIs and types: `io_uring_queue_init`, `io_uring_register_ring_fd`, `io_uring_close_ring_fd`, `io_uring_register_iowq_max_workers`, `io_uring_prep_nop`, `io_uring_submit`, and `io_uring_wait_cqe`. It tests normal-page and huge-page-sized entry counts plus SQPOLL.

Control flow: `test()` creates a registered-fd-only/no-mmap ring with optional SQPOLL, expects `io_uring_register_ring_fd()` to fail with `-EEXIST`, expects `io_uring_close_ring_fd()` to fail with `-EBADF` because the fd is already closed, then calls `io_uring_register_iowq_max_workers()` and requires nonzero returned worker limits. `test_nops()` submits and drains four ring-depths worth of NOPs in batches no larger than the SQ size. `main()` runs 8-entry normal, 8-entry SQPOLL, and 512-entry huge-page cases, skipping on unsupported no-mmap/registered-fd-only or huge page memory limits.

State and persistence: ring fd registration state is the primary persistent state. The test intentionally uses a ring whose normal fd is closed by setup semantics, then relies on the registered fd for further operations.

Dependencies and integration: requires registered-fd-only and no-mmap support; `-EINVAL` or `-ENOENT` marks unsupported. Huge-page-sized rings may skip with `-ENOMEM`.

Risks and test signals: incorrect `-EEXIST`/`-EBADF`, failed register after close, or inability to submit NOPs indicates registered-ring lifecycle regressions. Passing proves registered-fd-only rings remain operational without a regular ring fd.
