# sources/test-tools/liburing/test/mshot-shutdown-race.c

Purpose: stress reproducer for multishot recv racing with a send immediately followed by socket shutdown, ensuring neither data nor EOF events are lost.

Important APIs/types/functions: `io_uring_prep_recv_multishot`, `io_uring_setup_buf_ring`, `io_uring_buf_ring_add`, `io_uring_buf_ring_advance`, `IOSQE_BUFFER_SELECT`, `IORING_CQE_F_MORE`, `IORING_CQE_F_BUFFER`, `socketpair`, optional loopback TCP via `TEST_USE_INET`, and pthread barriers.

Control flow: a client thread waits on a barrier, sends one or two fixed-size messages, then `shutdown(SHUT_WR)`. For 10,000 iterations, main creates sockets, arms one multishot recv with provided buffers, releases the client, drains CQEs until EOF, replenishes buffers, verifies flags, and checks total bytes.

State and persistence behavior: no files. State is provided-buffer ownership, multishot continuation flags, socket shutdown state, and a watchdog alarm that detects stalls.

Dependencies and integration points: depends on AF_UNIX socketpair by default or AF_INET loopback when `TEST_USE_INET` is set, buf-ring support, and multishot receive semantics.

Risks and test signals: failures include missing `MORE` on data CQEs, buffer flag missing, EOF still marked `MORE`, wrong byte count, unexpected negative recv, or watchdog timeout.
