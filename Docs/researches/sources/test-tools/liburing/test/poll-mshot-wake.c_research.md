# sources/test-tools/liburing/test/poll-mshot-wake.c

Purpose: verifies multishot poll remains functional when polling the same eventfd used for io_uring CQ notifications.

Important APIs/types/functions: `eventfd`, `io_uring_register_eventfd`, `io_uring_prep_poll_multishot`, `io_uring_wait_cqe_timeout`, `IORING_CQE_F_MORE`, and `NR_LOOPS=2`.

Control flow: registers a nonblocking eventfd as the ring notification fd, arms multishot poll on that eventfd, then twice writes and drains the eventfd and waits for a poll CQE. The first CQE should have `MORE`; the second is expected to terminate without `MORE`.

State and persistence behavior: transient eventfd, ring eventfd registration, and multishot poll state.

Dependencies and integration points: depends on eventfd notification integration and poll wake path handling `EPOLL_URING_WAKE`.

Risks and test signals: failure indicates a stuck multishot poll, missing CQE within one second, wrong user_data/res, or incorrect `MORE` flag transition.
