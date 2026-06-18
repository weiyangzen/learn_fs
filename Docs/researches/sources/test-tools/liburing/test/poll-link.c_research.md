# sources/test-tools/liburing/test/poll-link.c

Purpose: validates linked poll plus link-timeout behavior for both timeout and ready-connection cases.

Important APIs/types/functions: pthread condition/barrier helpers, TCP loopback sockets, `t_bind_ephemeral_port`, `io_uring_prep_poll_add`, `io_uring_prep_link_timeout`, `IOSQE_IO_LINK`, `POLLIN`, `POLLHUP`, and `POLLERR`.

Control flow: a receiver thread listens on an ephemeral port, submits linked poll and timeout, and checks two CQEs against expected values. For no-connect, poll should be `-ECANCELED` and timeout `-ETIME`. For connect, poll should include `POLLIN` and timeout should be `-ECANCELED`. A sender thread connects only in the ready case.

State and persistence behavior: transient sockets and synchronization flags. No files.

Dependencies and integration points: depends on loopback TCP, helper ephemeral binding, and exact linked timeout cancellation semantics.

Risks and test signals: detects poll not canceled on timeout, timeout not canceled when poll completes, or mask mismatches when accepting a connection.
