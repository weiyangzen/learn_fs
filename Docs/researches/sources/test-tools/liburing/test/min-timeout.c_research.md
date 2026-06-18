# sources/test-tools/liburing/test/min-timeout.c

Purpose: tests `io_uring_submit_and_wait_min_timeout()` with pipe reads, staged writers, context switch expectations, and normal/deferred/SQPOLL rings.

Important APIs/types/functions: `io_uring_submit_and_wait_min_timeout`, `io_uring_prep_read`, `IORING_FEAT_MIN_TIMEOUT`, `IORING_SETUP_SINGLE_ISSUER`, `IORING_SETUP_DEFER_TASKRUN`, `IORING_SETUP_SQPOLL`, `getrusage(RUSAGE_THREAD)`, `mtime_since_now`, and `pthread_create`.

Control flow: `test()` initializes a ring, arms eight pipe reads, starts a writer that writes six buffers with a configured delay, waits with a total timeout and optional minimum wait, then counts CQEs and elapsed milliseconds. `main()` runs cases with no min timeout, 50 ms, 500 ms, and delayed-first-event variants across setup flags.

State and persistence behavior: no files. State includes pipe readiness, CQE accumulation, min timeout duration, and voluntary context-switch count.

Dependencies and integration points: depends on kernel min-timeout feature detection, pthread timing, and pipe read/write behavior.

Risks and test signals: failures include wrong CQE count, wait duration outside 25 percent tolerance, feature absence skip, or submit returning fewer requests than expected.
