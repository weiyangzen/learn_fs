# sources/test-tools/liburing/test/socket-rw.c

Purpose: baseline regression that a socket `readv` queued before a peer `writev` does not hang and both complete with the expected byte count.

Important APIs/types/functions: TCP loopback sockets, `io_uring_prep_readv`, `io_uring_prep_writev`, `io_uring_submit_and_wait`, `io_uring_for_each_cqe`, and helper nonblocking connect functions.

Control flow: creates a loopback TCP connection, queues a readv for 128 bytes on the accepted socket and a writev for 128 bytes on the connecting socket, submits both, and advances CQEs after both report exactly 128 bytes.

State/persistence behavior: no durable state; only socket queues and ring completions.

Dependencies/integration: exercises basic socket read/write via io_uring without feature gating.

Risks/test signals: failure is generally a hang, wrong CQE result, or incomplete CQE count.
