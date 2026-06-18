# sources/test-tools/liburing/test/poll-mshot-update.c

Purpose: stress-tests multishot poll update requests while many pipe polls are concurrently triggered.

Important APIs/types/functions: `io_uring_prep_poll_multishot`, `io_uring_prep_poll_update`, `IORING_POLL_UPDATE_EVENTS`, `IORING_TIMEOUT_UPDATE`, `IORING_CQE_F_MORE`, `RLIMIT_NOFILE`, pthread trigger thread, and `O_NONBLOCK`.

Control flow: first probes poll-update support by expecting `-ENOENT` for an update to a missing request. It then creates up to 5000 nonblocking pipes, arms multishot polls, and for each loop starts a thread that writes to 500 pipes while the main thread submits 500 update SQEs and drains both update and poll CQEs. It runs with CQ sizes 1024 and 8192.

State and persistence behavior: transient pipe arrays, trigger flags, multishot poll state, and update completions. No persistent files.

Dependencies and integration points: requires poll update support, high fd limits, pthreads, and CQSIZE support or fallback.

Risks and test signals: failures include lost update completions, stale non-MORE poll needing failed rearm, read errors other than EAGAIN, and concurrency races between updates and readiness.
