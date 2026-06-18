# sources/test-tools/liburing/test/large-resize.c

Purpose: exercises `io_uring_resize_rings()` while large CQE/SQE layouts are active, including fixed 32-byte CQEs, mixed CQE/SQE modes, pending SQEs, and wrapped CQ state.

Important APIs/types/functions: `io_uring_queue_init_params`, `io_uring_resize_rings`, `io_uring_prep_nop`, `io_uring_submit`, `io_uring_wait_cqe`, `io_uring_peek_cqe`, `__io_uring_flush_sq`, `IORING_SETUP_CQE32`, `IORING_SETUP_CQE_MIXED`, `IORING_SETUP_SQE128`, `IORING_SETUP_SQE_MIXED`, `IORING_SETUP_CQSIZE`, `IORING_SETUP_DEFER_TASKRUN`, and `IORING_SETUP_SINGLE_ISSUER`.

Control flow: `main()` runs five subtests. CQE32 and mixed-CQE tests submit NOPs, resize the CQ from 8 to 16 entries, then validate `user_data`. The wrapping test uses a four-entry ring, consumes early CQEs to force head/tail wrap, resizes, and verifies only the last two completions remain. SQE128 and SQE-mixed tests queue NOPs with extended command bytes, flush SQ state before submit, resize, then submit and reap.

State and persistence behavior: all state is transient ring memory, especially SQ/CQ mapping size, CQ head/tail wrapping, pending SQEs, and 32-byte CQE payload preservation. No filesystem persistence is used.

Dependencies and integration points: depends on newer kernel/liburing resize and large-entry support. `-EINVAL` at setup or resize is treated as skip in feature-probe paths. It integrates with `helpers.h` for `T_EXIT_*` status constants.

Risks and test signals: catches data corruption during remap/copy of large CQEs or SQEs, bad CQ ordering across resize, and lost completions after wrap. Success is exact `user_data` preservation and expected completion counts; failures print corruption markers.
