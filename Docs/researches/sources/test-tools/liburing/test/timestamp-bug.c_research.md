# sources/test-tools/liburing/test/timestamp-bug.c

Purpose: regression test for socket transmit timestamp retrieval when the socket error queue contains both timestamp messages and real errors. It ensures `SOCKET_URING_OP_TX_TIMESTAMP` can retry/scan the current skb list rather than being confused by mixed error-queue contents.

Important APIs/types/functions: `create_sock_with_timestamps_and_errors`, `socket(AF_INET, SOCK_DGRAM)`, `setsockopt(SO_TIMESTAMPING)`, `setsockopt(IP_RECVERR)`, `sendto`, `recvmsg(MSG_ERRQUEUE)`, `IORING_SETUP_CQE32`, `IORING_OP_URING_CMD`, and `SOCKET_URING_OP_TX_TIMESTAMP`.

Control flow: helper creates a UDP socket with software TX timestamps and IP error queue reporting enabled, creates a receiving UDP socket on loopback, sends two packets to generate TX timestamps, then sends to closed port 9 to generate an error. Main creates a CQE32 ring, submits one socket uring command for TX timestamp retrieval, and treats `-EOPNOTSUPP` as skip. It then drains one error-queue message with `recvmsg`.

State/persistence behavior: no durable state. Runtime state is kernel socket error queue contents and CQE32 timestamp payload handling.

Dependencies/integration: uses IPv4 loopback UDP, Linux timestamping options, error queue support, socket uring commands, and CQE32 layout.

Risks/test signals: assumes localhost networking and port 9 closed enough to generate an error. Failures show as unsupported ring setup, wait errors, or timestamp command errors other than `-EOPNOTSUPP`.
