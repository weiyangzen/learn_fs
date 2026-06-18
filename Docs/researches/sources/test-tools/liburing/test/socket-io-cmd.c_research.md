# sources/test-tools/liburing/test/socket-io-cmd.c

Purpose: validates io_uring socket ioctl command operations (`SIOCINQ`, `SIOCOUTQ`) against normal ioctl behavior and internal socket buffer accounting.

Important APIs/types/functions: `io_uring_prep_cmd_sock`, `SOCKET_URING_OP_SIOCINQ`, `SOCKET_URING_OP_SIOCOUTQ`, `ioctl(SIOCINQ/SIOCOUTQ)`, stream/datagram socket pairs, raw sockets, and `t_create_ring`.

Control flow: `run_test()` creates a stream or datagram socket pair, writes a known message, queries receive and send queue sizes through io_uring commands, and verifies their sum equals written bytes. `run_test_raw()` opens a raw TCP socket when permitted and compares io_uring command results directly with ioctl values, retrying once for racing queue changes.

State/persistence behavior: state is socket queue occupancy. `no_io_cmd` records lack of socket io command support.

Dependencies/integration: needs socket command support, helper socket pairs, and root/capabilities for raw socket coverage. Unsupported raw socket creation is skipped.

Risks/test signals: detects incorrect queue counts, unsupported command handling, raw socket mismatch, or CQE user data/result corruption.
