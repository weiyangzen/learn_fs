# sources/test-tools/liburing/test/pipe-eof.c

Purpose: verifies that reads from a pipe whose writer has closed complete with EOF (`res == 0`) instead of waiting indefinitely.

Important APIs/types/functions: `pthread_create`, `io_uring_prep_read`, `io_uring_submit`, `io_uring_wait_cqe`, pipe fds, and `BUFSIZE`.

Control flow: a thread writes a test string to the pipe and closes the write end. Main repeatedly submits pipe reads via io_uring until a CQE returns zero, treating negative results as errors.

State and persistence behavior: transient pipe, thread, and static buffer only.

Dependencies and integration points: depends on standard pipe EOF semantics and io_uring read completion.

Risks and test signals: failure is any read error, submit/wait failure, or hang before EOF. `-ENOMEM` ring setup skips.
