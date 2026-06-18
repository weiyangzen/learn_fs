# sources/test-tools/liburing/test/shutdown.c

Purpose: checks `IORING_OP_SHUTDOWN` and subsequent socket write behavior: after shutting down write side, `writev` should fail with `-EPIPE`.

Important APIs/types/functions: `io_uring_prep_shutdown`, `io_uring_prep_writev`, TCP loopback sockets, `shutdown(SHUT_WR)`, `TCP_NODELAY`, `SIGPIPE` handler, and helper nonblocking connect utilities.

Control flow: sets up a loopback TCP connection, waits for connect completion via `SO_ERROR`, initializes a ring, submits shutdown on the client fd, accepts `-EINVAL` as unsupported, then submits `writev` and requires `-EPIPE`.

State/persistence behavior: only socket state is mutated; no files are written. `SIGPIPE` is ignored through a no-op handler so the process observes the CQE error.

Dependencies/integration: depends on TCP loopback, io_uring shutdown support, and correct socket error propagation through io_uring writev.

Risks/test signals: failures include shutdown unsupported, shutdown returning another error, write succeeding, or write returning an errno other than `-EPIPE`.
