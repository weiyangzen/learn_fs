<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/iopoll-sync.c -->
## sources/test-tools/liburing/test/iopoll-sync.c

Purpose: verifies uring socket command operations on an IOPOLL ring for files that do not support normal polled IO.

Important APIs/types/functions: `io_uring_prep_cmd_sock`, `SOCKET_URING_OP_GETSOCKOPT`, `SOCKET_URING_OP_SETSOCKOPT`, `IORING_SETUP_IOPOLL`, `IOSQE_IO_LINK`, and `io_uring_cqe_iter`.

Control flow: the test creates a TCP socket, initializes `SO_REUSEADDR` to zero, creates an IOPOLL ring, queues linked getsockopt, setsockopt, and getsockopt socket commands, submits all three, then iterates CQEs to verify the first read returns zero, the set succeeds, the second read returns one, and no extra CQEs exist. Unsupported command results skip.

State and persistence behavior: socket option state changes from 0 to 1. The ring CQ is traversed using the CQE iterator without explicit advance in this file.

Dependencies and integration points: integrates uring command socket operations with IOPOLL rings and linked CQE ordering.

Risks: command support is kernel-dependent. The test assumes CQEs appear in link order.

Test signals: pass means socket uring commands work and synchronize correctly on an IOPOLL ring.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/iopoll-sync.c -->
