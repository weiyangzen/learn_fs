# sources/test-tools/liburing/test/reg-reg-ring.c

Purpose: tests `IORING_REGISTER_USE_REGISTERED_RING` behavior for a ring fd explicitly registered with the kernel. It verifies registration, duplicate registration, close semantics, and continued register operations after closing the normal ring fd.

Important APIs and types: `io_uring_queue_init`, ring feature bit `IORING_FEAT_REG_REG_RING`, `io_uring_register_ring_fd`, `io_uring_unregister_ring_fd`, `io_uring_close_ring_fd`, and `io_uring_register_iowq_max_workers`.

Control flow: `main()` initializes a ring and skips if `IORING_FEAT_REG_REG_RING` is absent. Before registration, `io_uring_close_ring_fd()` and `io_uring_unregister_ring_fd()` must return `-EINVAL`. Registering must return `1`; duplicate registering must return `-EEXIST`. A normal register operation (`io_uring_register_iowq_max_workers`) must work before closing the ring fd. Closing must return `1`; the same register operation must still work after close through the registered-ring path. A second close must return `-EBADF`.

State and persistence: ring fd registration status transitions from unregistered to registered to closed-normal-fd while retaining registered-ring usability. Worker limit values are used as proof of register-call execution.

Dependencies and integration: feature-gated by `IORING_FEAT_REG_REG_RING`. Uses helpers for standard exit codes.

Risks and test signals: wrong lifecycle return codes or inability to register after close indicate registered-ring fd regressions. Passing confirms liburing can operate register opcodes on registered rings after closing the original fd.
