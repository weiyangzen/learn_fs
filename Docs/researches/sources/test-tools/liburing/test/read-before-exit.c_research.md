# sources/test-tools/liburing/test/read-before-exit.c

Purpose: reproduces a thread-exit race where I/O is submitted from a pthread that immediately returns. It verifies queued reads survive the submitting thread's sudden exit and that ring teardown does not trip over pending timerfd reads. The test references liburing issue 582.

Important APIs and types: `pthread_create`, `pthread_join`, `timerfd_create`, `io_uring_prep_read`, `io_uring_submit`, `io_uring_peek_cqe`, `t_create_ring_params`, and setup flags `IORING_SETUP_IOPOLL` and `IORING_SETUP_SQPOLL`. `struct data` carries the ring, two timerfds, and two read buffers into the submit thread.

Control flow: `submit()` queues two timerfd reads and expects `io_uring_submit()` to submit both. If submit does not return 2, it peeks for an `-EOPNOTSUPP` CQE and records `no_iopoll` rather than failing on kernels without submit-all-on-error behavior. `test()` creates the ring with requested flags, creates two timerfds, starts and joins the submitter, then exits the queue and closes fds. `main()` runs 1000 plain iterations, up to 1000 IOPOLL iterations unless unsupported, and 100 SQPOLL iterations.

State and persistence: thread-local submission is intentionally short lived. The ring and timerfds persist in the parent thread across submitter exit. `no_iopoll` stops repeated unsupported IOPOLL loops.

Dependencies and integration: requires pthreads and timerfd. It uses helper ring setup so unsupported setup flags can skip individual loops without failing the full test.

Risks and test signals: failures include submit counts other than expected, unsupported behavior not represented as `-EOPNOTSUPP`, or crashes during queue exit. Passing is mostly stability oriented: submitted work remains owned by the ring, not by the exiting submit thread.
