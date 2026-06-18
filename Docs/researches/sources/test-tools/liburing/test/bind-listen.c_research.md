# sources/test-tools/liburing/test/bind-listen.c

Purpose: tests TCP socket setup and data flow performed through io_uring socket/bind/listen/accept/connect/send/recv commands, including direct/fixed-file sockets. Key APIs include `io_uring_prep_socket_direct`, `io_uring_prep_cmd_sock`, `io_uring_prep_bind`, `io_uring_prep_listen`, `io_uring_prep_accept_direct`, `io_uring_prep_cmd_getsockname`, and fixed-fd installation fallback.

Control flow: `main` probes `IORING_OP_LISTEN`, runs the good server/client path under normal, defer-taskrun, and SQPOLL flags, then checks malformed bind/listen/sockname cases for expected errors. State is transient ring fixed-file and socket state; `no_getsockname` persists old-kernel fallback detection. Risks are kernel feature drift, network timing, wrong CQE errors, or incorrect peer/data validation.
