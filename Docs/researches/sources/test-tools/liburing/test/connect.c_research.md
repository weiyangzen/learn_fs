# sources/test-tools/liburing/test/connect.c

Purpose: covers io_uring connect success, refused connection, async connect, linked timeout cancellation, SQPOLL, and defer-taskrun. Key APIs are `io_uring_prep_connect`, `io_uring_prep_poll_add`, `io_uring_prep_link_timeout`, `IOSQE_ASYNC`, `IOSQE_IO_LINK`, `getsockopt(SO_ERROR)`, and TCP socket setup.

Control flow: for each ring mode, pick a loopback port, verify no-peer `-ECONNREFUSED`, test successful sync/async connects, then fill a zero-backlog listener and require linked connect to cancel with timeout `-ETIME`. State is transient sockets and random port. Risks are TCP timing/settings, unsupported modes, and incorrect link-timeout cancellation.
