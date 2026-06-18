# sources/test-tools/liburing/examples/io_uring-udp.c

## sources/test-tools/liburing/examples/io_uring-udp.c

Purpose: UDP echo server using multishot `recvmsg`, provided buffer rings, fixed files, and sendmsg replies.

Important APIs/types/functions: `struct ctx`, `struct sendmsg_ctx`; `setup_buffer_pool`, `setup_context`, `setup_sock`, `add_recv`, `process_cqe_recv`, `process_cqe_send`, `process_cqe`; `io_uring_prep_recvmsg_multishot`, `io_uring_recvmsg_validate`, `io_uring_recvmsg_payload`, `io_uring_prep_sendmsg`, fixed file registration.

Control flow: parse IPv4/IPv6/port/buffer-size/verbose options, bind UDP socket, initialize ring with enlarged CQ, register buffer ring, register socket as fixed file, arm multishot recv, then submit-and-wait. Recv CQEs validate selected buffer and recvmsg metadata, optionally log peer, prepare a sendmsg back to source, and rearm if multishot ended. Send CQEs recycle buffers.

State and persistence: memory-mapped region stores both buffer ring descriptors and payload buffers. Socket is registered fixed file. No file persistence.

Dependencies/integration: kernel >= 6.0 for buffer rings/multishot recvmsg; liburing helpers for recvmsg parsing; UDP networking.

Risks: control length is zero, so ancillary data is ignored. Truncated names/payloads are dropped. Uses `cqe->flags >> 16` instead of named shift in one place. Infinite server loop lacks graceful shutdown cleanup except error path.

Test signals: binding log, verbose receive logs, echo behavior from UDP clients, build in examples.
