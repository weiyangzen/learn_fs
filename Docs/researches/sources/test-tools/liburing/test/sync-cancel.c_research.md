# sources/test-tools/liburing/test/sync-cancel.c

Purpose: tests `io_uring_register_sync_cancel()` for user-data cancellation, fd cancellation, cancel-all, async/sync reads, per-op cancellation, and timeout behavior.

Important APIs/types/functions: `io_uring_sync_cancel_reg`, `io_uring_register_sync_cancel`, `IORING_ASYNC_CANCEL_ALL`, `IORING_ASYNC_CANCEL_FD`, `IORING_ASYNC_CANCEL_OP`, `IORING_OP_READ`, pipe reads, and `IOSQE_ASYNC`.

Control flow: `test_sync_cancel()` queues one or four blocking pipe reads, configures cancel by user_data or fd and optional all flag, calls sync cancel, then waits for all CQEs to have negative results. `test_sync_cancel_timeout()` queues a read and calls per-op cancel with a tiny timeout, accepting async races where cancel succeeds or times out. `main()` runs a matrix across sync/async, all/single, address/fd, and per-op timeout cases.

State/persistence behavior: pipe fds and pending read requests are the mutable state. Feature flags `no_sync_cancel` and `no_sync_cancel_op` record unsupported kernels.

Dependencies/integration: requires sync-cancel registration support; older kernels skip on `-EINVAL`.

Risks/test signals: catches uncanceled reads, nonnegative CQEs, wrong timeout/cancel errno, missing per-op support handling, and races around async cancellation posting completions.
