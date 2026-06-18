# sources/test-tools/liburing/test/cq-size.c

Purpose: tests explicit CQ sizing via `IORING_SETUP_CQSIZE`. Key APIs are `io_uring_queue_init_params`, `io_uring_params.cq_entries`, and `io_uring_queue_exit`.

Control flow: request a 64-entry CQ with four SQ entries and verify the kernel gives at least 64; then request zero CQ entries and require `-EINVAL`. State is ring setup parameters only. Risks are unsupported kernels, ignored CQ sizing, or acceptance of invalid zero size.
