<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/files-exit-hang-timeout.c -->
## sources/test-tools/liburing/test/files-exit-hang-timeout.c

Purpose: companion exit-hang regression using a long linked timeout instead of poll before accept.

Important APIs/types/functions: `add_timeout`, `add_accept`, `setup_io_uring`, `io_uring_prep_timeout`, `io_uring_prep_accept`, `IOSQE_IO_LINK`, fixed port scan from `PORT`, and `alarm`.

Control flow: the test binds a nonblocking TCP listener to the first available port in a 100-port range, initializes a ring, links a 300-second timeout to an accept request, submits both, sets a one-second alarm that exits successfully, and waits for completion.

State and persistence behavior: the ring has a long pending linked timeout and an accept. The socket and ring are intentionally left pending until alarm-driven process exit or normal cleanup.

Dependencies and integration points: exercises timeout linked to socket accept and task file table cleanup on process exit.

Risks: hardcoded port range can be exhausted and cause skip. Like the poll variant, success is primarily absence of hang.

Test signals: pass means pending timeout/accept chains do not deadlock exit cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/files-exit-hang-timeout.c -->
