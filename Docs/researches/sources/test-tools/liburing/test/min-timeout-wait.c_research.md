# sources/test-tools/liburing/test/min-timeout-wait.c

Purpose: validates `io_uring_wait_cqes_min_timeout()` behavior for minimum wait windows with already-ready CQEs, delayed pipe writes, no CQEs, and different ring modes.

Important APIs/types/functions: `io_uring_wait_cqes_min_timeout`, `io_uring_prep_read`, `io_uring_prep_nop`, `io_uring_cq_advance`, `IORING_FEAT_MIN_TIMEOUT`, `IORING_SETUP_SINGLE_ISSUER`, `IORING_SETUP_DEFER_TASKRUN`, `IORING_SETUP_SQPOLL`, `pthread_barrier_t`, and `mtime_since_now`.

Control flow: helper threads write to pipes after configured delays. The tests cover full availability, partial availability within min timeout, late first event, no events, and min-wait values larger or equal to the total wait. `main()` runs the matrix on normal, deferred-taskrun, and SQPOLL rings when available.

State and persistence behavior: transient pipes, ring CQ state, and elapsed time checks. No persistent files.

Dependencies and integration points: uses `t_create_ring_params` to probe setup, feature flag `IORING_FEAT_MIN_TIMEOUT`, pthreads, and helper timing functions.

Risks and test signals: failures are wrong timeout duration, unexpected `-ETIME` or success return, not enough CQEs advanced, or inconsistent behavior across supported ring modes.
