# sources/test-tools/liburing/test/socket-getsetsock-cmd.c

Purpose: compares socket getsockopt/setsockopt operations issued through io_uring socket commands with equivalent synchronous system calls.

Important APIs/types/functions: `io_uring_prep_cmd_sock`, `SOCKET_URING_OP_GETSOCKOPT`, `SOCKET_URING_OP_SETSOCKOPT`, `SO_RCVBUF`, `SO_PEERNAME`, `SO_REUSEPORT`, `TCP_USER_TIMEOUT`, `IOSQE_ASYNC`, and helper `t_create_socket_pair`.

Control flow: creates a connected socket pair, writes data, and runs getsockopt tests for peer name and receive buffer in sync/async modes. It then sets `SO_REUSEPORT` values and `TCP_USER_TIMEOUT` values via io_uring commands in sync/async modes and verifies regular `getsockopt` observes the same state.

State/persistence behavior: state is socket options and queued data inside the socket pair. Global `no_sock_opt` records unsupported command behavior.

Dependencies/integration: requires kernel socket command support and TCP socket option behavior. `-EOPNOTSUPP`/`-EINVAL` can skip unsupported paths.

Risks/test signals: detects wrong result lengths, mismatched option values, unsupported command errno, or async command behavior diverging from sync behavior.
