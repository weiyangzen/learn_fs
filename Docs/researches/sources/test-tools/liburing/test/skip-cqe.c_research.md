# sources/test-tools/liburing/test/skip-cqe.c

Purpose: validates `IOSQE_CQE_SKIP_SUCCESS` behavior for successful linked chains, failed linked chains, link timeouts, timeout cancellation, and hardlink chains.

Important APIs/types/functions: `IOSQE_CQE_SKIP_SUCCESS`, `IOSQE_IO_LINK`, `IOSQE_IO_HARDLINK`, `IOSQE_ASYNC`, `io_uring_prep_link_timeout`, `io_uring_prep_nop`, `io_uring_prep_read`, `IORING_FEAT_CQE_SKIP`, and pipe-backed failure request prep.

Control flow: after feature gating, `main()` runs success chains with and without the last CQE skipped, failure chains where a NULL write fails, link-timeout cancellation cases across timeout positions and async mode, timeout-fire cases with skip flags on main/timeout SQEs, and hardlink matrices across fail/skip positions and last-link marking. Each helper verifies exactly the expected CQEs remain.

State/persistence behavior: only pipe fds, ring CQ state, and request flags are used. The pipe read in timeout tests provides a cancellable pending operation.

Dependencies/integration: depends on CQE skip feature support and precise link/hardlink cancellation semantics.

Risks/test signals: extra CQEs, missing failure CQEs, wrong `user_data`, wrong cancellation errno, or success CQEs that should have been skipped all fail the test.
