# sources/test-tools/liburing/test/recv-msgall.c

Purpose: checks `MSG_WAITALL` on datagram sockets for `recv` and `recvmsg`. It documents and enforces datagram semantics: even with `MSG_WAITALL` and two sends, one receive should complete with one datagram, here half of the full integer buffer.

Important APIs and types: UDP socket bind/connect, `io_uring_prep_recv`, `io_uring_prep_recvmsg`, `io_uring_prep_send`, `MSG_WAITALL`, `pthread_barrier_t`, `t_bind_ephemeral_port`, and `struct msghdr`.

Control flow: `recv_fn()` creates a ring and UDP socket, binds an ephemeral port, submits one wait-all receive or recvmsg, then releases the sender through a barrier. `do_send()` connects a UDP socket to that port and submits two io_uring sends, each for half the buffer, with a sleep between submissions. `do_recv()` waits for the receive CQE and requires `MAX_MSG * sizeof(int) / 2`, because one datagram is delivered per receive. `test()` runs recv and recvmsg variants.

State and persistence: global `bind_port` communicates the receiver's ephemeral port to the sender after the barrier. `struct recv_data` stores the barrier, `use_recvmsg`, and persistent `msghdr` for recvmsg validation lifetime.

Dependencies and integration: uses UDP loopback and pthread barriers. `-EINVAL` for recv or send is treated as unsupported.

Risks and test signals: receiving the full two-send size would violate the expected datagram behavior for this test, while shorter or negative results indicate recv bugs. Passing shows io_uring preserves datagram message boundaries with `MSG_WAITALL`.
