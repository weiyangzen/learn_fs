<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/io-cancel.c -->
## sources/test-tools/liburing/test/io-cancel.c

Purpose: broad cancellation suite for normal IO, partial cancels, cross-ring isolation, forked cancellation, inflight exit, and SQPOLL/io-wq cleanup.

Important APIs/types/functions: `start_io`, `wait_io`, `do_io`, `start_cancel`, `test_io_cancel`, `test_dont_cancel_another_ring`, `test_cancel_req_across_fork`, `test_cancel_inflight_exit`, `test_sqpoll_cancel_iowq_requests`, `io_uring_prep_cancel64`, `io_uring_prep_poll_add`, and `io_uring_prep_timeout`.

Control flow: `main` first runs targeted pipe/poll/fork/SQPOLL cleanup scenarios, then creates an O_DIRECT test file and buffers. It runs eight combinations of read/write, full/partial cancel, and async/non-async cancel. IO is timed to allow some requests to start before cancel SQEs are submitted; completions are validated based on whether partial cancellation should leave odd-numbered IO intact.

State and persistence behavior: global `vecs` backs the file IO matrix. Pipes, forked processes, and temporary `.io-cancel-test` file create transient state; the file is unlinked on exit.

Dependencies and integration points: integrates cancel-by-user_data, async cancel, direct IO, pipes, fork sharing, linked poll/timeout chains, SQPOLL, and io-wq references.

Risks: cancellation timing is inherently race-sensitive and accepts several legitimate results such as `-ECANCELED`, `-EINTR`, `-EALREADY`, or successful completion in targeted cases.

Test signals: pass means cancellation is scoped, does not cross rings accidentally, handles fork/exit, and leaves uncanceled IO valid.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/io-cancel.c -->
