# sources/test-tools/liburing/test/timestamp.c

Purpose: socket TX timestamp coverage for io_uring socket commands. It verifies timestamp CQEs for IPv6 TCP send paths, including SCHED, software send, ACK timestamp types, option-id progression, and both CQE32 and mixed-CQE modes.

Important APIs/types/functions: `struct ctx`, `struct send_req`, `validate_key`, `test_prep_sock`, `queue_ts_cmd`, `queue_send`, `get_tstype_name`, `do_test`, `resolve_hostname`, `do_listen`, `do_main`, `io_uring_prep_sendmsg`, `IORING_OP_URING_CMD`, `SOCKET_URING_OP_TX_TIMESTAMP`, `IORING_SETUP_CQE32`, `IORING_SETUP_CQE_MIXED`, `IORING_CQE_F_MORE`, `IORING_CQE_F_32`, and `struct io_timespec`.

Control flow: main binds a loopback IPv6 listener and runs TCP timestamp scenarios first with CQE32 and then mixed CQEs. Each `do_test` creates a timestamp-enabled socket, sends one payload with `sendmsg`, waits for the send CQE, sleeps briefly for timestamp availability, submits the TX timestamp uring command, and iterates all returned CQEs. It counts expected timestamp types from `SOF_TIMESTAMPING_TX_*` flags and validates timestamp keys advance by payload length for streams unless explicit cmsg option IDs are used.

State/persistence behavior: state is socket timestamp option configuration, saved timestamp key/type globals, and listener file descriptor lifetime. No filesystem state.

Dependencies/integration: requires IPv6 loopback, TCP_NODELAY, Linux timestamping ancillary data definitions, CQE32 or mixed CQE support, and liburing helper `t_create_ring`.

Risks/test signals: skips if timestamp command is unsupported. Failures include missing/extra timestamp CQEs, wrong key progression, missing CQE32 flag in mixed mode, error CQE results, or inability to bind/connect loopback.
