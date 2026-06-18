# sources/test-tools/liburing/test/poll-update-trigger.c

Purpose: verifies that an existing `POLL_ADD` request can be updated to a newly-triggering event mask and that both the update SQE and the original poll SQE complete with the expected results. The specific regression target is a poll initially armed on the pipe write end for `POLLIN`, which should not fire, then changed with `io_uring_prep_poll_update()` to `POLLOUT`, which should fire immediately.

Important APIs and types: `io_uring_queue_init`, `io_uring_get_sqe`, `io_uring_prep_poll_add`, `io_uring_prep_poll_update`, `io_uring_submit`, `io_uring_wait_cqe`, `io_uring_cqe_seen`, `struct io_uring`, `struct io_uring_sqe`, `struct io_uring_cqe`, `pipe`, and poll masks from `<poll.h>`. `IORING_POLL_UPDATE_EVENTS` is the key update mode.

Control flow: initialize a four-entry ring, create a pipe, submit the non-triggering `POLL_ADD` with `user_data = 1`, submit the poll update with `user_data = 2`, then wait for two CQEs in any order. The original request must return `POLLOUT`; the update request must return `0`.

State and persistence: only kernel poll state associated with the pending SQE persists between submissions. The test uses `user_data` as the only durable correlation state and does not clean up the ring or pipe explicitly before process exit.

Dependencies and integration: depends on liburing poll update support and pipe write readiness semantics. It integrates with the liburing test harness via `helpers.h` exit codes and skips when extra command-line arguments are supplied.

Risks and test signals: failures indicate poll-update event masks are not applied, completion ordering assumptions are wrong, or the original poll does not complete after the update. A passing run produces two CQEs with `res` values `POLLOUT` and `0`; queue setup or pipe failures are hard failures.
