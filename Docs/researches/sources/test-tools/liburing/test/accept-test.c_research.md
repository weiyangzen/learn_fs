<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/accept-test.c -->
## sources/test-tools/liburing/test/accept-test.c

Purpose: small focused accept smoke test.

Important APIs/types/functions: single `main` creates a listening socket, initializes an io_uring, prepares `IORING_OP_ACCEPT`, connects a client, waits for completion, and validates the accepted descriptor.

Control flow: skip on arguments, set up local TCP listener, queue accept SQE, submit, initiate client connection, wait for CQE, check nonnegative result or supported skip error, close descriptors, and tear down the ring.

State and persistence behavior: transient listener, client, accepted socket, and ring. No persistent state.

Dependencies and integration points: depends on socket helpers, `io_uring_prep_accept`, submit/wait APIs, and CQE result semantics.

Risks: local port allocation and connection timing are the main external risks. Unsupported accept opcode should be represented as skip rather than failure.

Test signals: basic confidence that accept SQEs complete and return usable fds.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/accept-test.c -->
