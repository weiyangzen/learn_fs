# sources/test-tools/liburing/test/poll-cancel.c

Purpose: tests basic poll remove completion ordering and a child-exit cleanup path involving timeouts linked to ring-fd polling.

Important APIs/types/functions: `io_uring_prep_poll_add`, `io_uring_prep_poll_remove`, `io_uring_sqe_set_data`, `io_uring_cqe_get_data`, `io_uring_prep_timeout`, `io_uring_prep_link_timeout`, `fork`, `waitpid`, and `alarm`.

Control flow: the first test arms a poll on a pipe, submits a poll remove keyed by the poll's user data pointer, and waits for both cancel and poll CQEs, accepting either order with exact results. The second forks a child that submits a timeout, a linked poll on another ring fd, and a link timeout, then exits without cleanup so process exit cancels everything.

State and persistence behavior: transient pipes, rings, and child process state only.

Dependencies and integration points: depends on poll cancel semantics and kernel cleanup of ring resources on process exit.

Risks and test signals: failures are cancel CQE nonzero, poll CQE not `-ECANCELED`, alarm timeout, or child cleanup causing nonzero exit.
