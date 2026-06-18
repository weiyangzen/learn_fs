# sources/test-tools/liburing/test/poll-race.c

Purpose: stress test for multiple concurrent receives on the same socket when readiness wakeups race.

Important APIs/types/functions: `socketpair`, `io_uring_prep_recv`, `io_uring_submit`, `io_uring_wait_cqe`, pthread barrier, and `NREQS=64`.

Control flow: initializes one ring, then 1000 times creates a socketpair, starts a writer thread, queues 64 recv SQEs on one socket, releases the writer, submits all requests, and waits for 64 completions.

State and persistence behavior: transient socketpairs and a shared barrier. No files.

Dependencies and integration points: depends on PF_LOCAL stream socket readiness and io_uring receive poll-wakeup internals.

Risks and test signals: failure means a receive stalled or submit count was short under racing wakeups; CQE result contents are not deeply validated here.
