# sources/test-tools/liburing/test/send_recv.c

Purpose: exercises io_uring UDP send/recv paths with normal buffers, buffer selection, registered receive fds, SQPOLL, async submission, and vector send variants.

Important APIs/types/functions: `io_uring_prep_recv`, `io_uring_prep_send`, `IOSQE_FIXED_FILE`, `IOSQE_ASYNC`, `IOSQE_BUFFER_SELECT`, `IORING_CQE_F_SOCK_NONEMPTY`, `IORING_SETUP_SQPOLL`, `IORING_FEAT_SQPOLL_NONFIXED`, and `IORING_SETUP_SUBMIT_ALL` invalid sendmsg/recvmsg checks.

Control flow: a receiver thread sets up a UDP socket bound to localhost, optionally registers it, queues a recv, unlocks the sender, and verifies completion length/data. The sender creates a connected UDP socket and submits send, two-iovec, or 32-iovec send. `main()` initializes a patterned 4 KiB payload, checks invalid NULL msg cases return `-EFAULT`, then runs a matrix across SQPOLL, registration, async, provided buffers, and vector send.

State/persistence behavior: no persistent state; process-global payload `str` is used as the expected data and `no_send_vec` records kernels without vector send support.

Dependencies/integration: depends on pthread synchronization, localhost UDP port 10202, liburing helpers, optional SQPOLL nonfixed support, and buffer selection behavior.

Risks/test signals: failures include wrong lengths, data mismatch, ENOBUFS flag mistakes, unsupported vector sends, bad invalid-pointer errno, and races around fixed port reuse.
