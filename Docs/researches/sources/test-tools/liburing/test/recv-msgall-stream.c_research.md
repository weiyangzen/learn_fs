# sources/test-tools/liburing/test/recv-msgall-stream.c

Purpose: verifies `MSG_WAITALL` behavior for stream sockets for both `recv` and `recvmsg`, comparing io_uring operations with synchronous system calls. The sender splits one logical message into two sends; the receiver must still obtain the full requested length.

Important APIs and types: `io_uring_prep_recv`, `io_uring_prep_recvmsg`, `io_uring_prep_send`, `MSG_WAITALL`, `pthread_mutex_t`, TCP socket/listen/accept/connect, `t_bind_ephemeral_port`, and `struct msghdr`/`struct iovec`.

Control flow: receiver setup binds an ephemeral localhost TCP port and unlocks a mutex to let the sender connect. `recv_prep()` accepts a connection, submits either `recv` or `recvmsg` with `MSG_WAITALL`, and returns the accepted fd. `do_send()` connects and sends the integer buffer as two half-size io_uring sends separated by a short sleep. `do_recv()` waits for the single receive CQE and requires the full `MAX_MSG * sizeof(int)` result. `recv_sync()` performs the same wait-all receive using synchronous `recv` or `recvmsg`. `test()` runs four combinations: io_uring recv, io_uring recvmsg, sync recv, and sync recvmsg.

State and persistence: `struct recv_data` carries synchronization state, selected receive API, and port. The receive buffer is stack-local and validated after completion for the 0..127 integer pattern.

Dependencies and integration: uses TCP loopback, pthreads, and liburing send/recv support. `-EINVAL` for io_uring receive or send is treated as unsupported skip within that path.

Risks and test signals: partial reads, content mismatch, socket synchronization bugs, or unsupported operations not handled as skips fail. Passing confirms io_uring stream `MSG_WAITALL` waits across multiple sends like synchronous APIs.
