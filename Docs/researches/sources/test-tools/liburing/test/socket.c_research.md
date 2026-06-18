# sources/test-tools/liburing/test/socket.c

Purpose: tests `IORING_OP_SOCKET` socket creation followed by connect/send, including direct descriptor allocation and SQPOLL receive combinations.

Important APIs/types/functions: `io_uring_prep_socket`, `io_uring_prep_socket_direct`, `io_uring_prep_connect`, `io_uring_prep_send`, `io_uring_prep_recv`, `IOSQE_FIXED_FILE`, `IORING_FILE_INDEX_ALLOC`, `IORING_SETUP_SQPOLL`, `IORING_FEAT_SQPOLL_NONFIXED`, and `io_uring_register_files`.

Control flow: a receiver thread binds an ephemeral UDP port, optionally registers the receive fd, queues recv, and verifies the received string. The sender either uses `IORING_OP_SOCKET`/direct socket to create a UDP socket or falls back to normal socket+send if unsupported, connects to the receiver, and sends the string. `main()` runs normal, SQPOLL registered/nonregistered, direct fixed index, direct allocated index, and bad socket-family validation.

State/persistence behavior: state is UDP socket endpoints, global port `g_port`, and optional fixed-file slot. No persistent files.

Dependencies/integration: depends on socket opcode support for full coverage, but falls back when unavailable. It uses pthread synchronization and helper socket binding.

Risks/test signals: detects unsupported opcode handling, direct descriptor misuse, bad fixed-file flags, invalid family errno (`-EAFNOSUPPORT`), and payload/length mismatch.
