# sources/test-tools/liburing/test/shared-wq.c

Purpose: tests workqueue sharing setup through `IORING_SETUP_ATTACH_WQ`, including rejection of non-ring descriptors and successful attachment to a real ring.

Important APIs/types/functions: `io_uring_queue_init_params`, `IORING_SETUP_ATTACH_WQ`, `io_uring_params.wq_fd`, and `io_uring_queue_exit`.

Control flow: `main()` creates a base ring, calls `test_attach_invalid(2)` expecting `-EINVAL` when attaching to stdout, then calls `test_attach()` with the base ring fd and accepts `-EINVAL` as unsupported sharing or zero as success.

State/persistence behavior: only kernel ring/workqueue state is involved. No files or sockets persist.

Dependencies/integration: exercises ring setup parameter validation and shared worker-pool attachment. It does not queue I/O.

Risks/test signals: detects acceptance of invalid `wq_fd`, unexpected setup errno, or inability to attach where supported. It treats missing feature support as a passing skip-style path.
