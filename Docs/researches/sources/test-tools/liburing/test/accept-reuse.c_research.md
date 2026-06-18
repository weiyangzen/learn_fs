<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/accept-reuse.c -->
## sources/test-tools/liburing/test/accept-reuse.c

Purpose: regression test for manually reusing an SQE/SQ array slot for accept submission while relying on `IORING_FEAT_SUBMIT_STABLE`.

Important APIs/types/functions: global `struct io_uring io_uring`; `sys_io_uring_enter` wraps the internal syscall helper; `submit_sqe` writes `sq->array[tail & mask] = 0`, release-stores `ktail`, and enters the ring directly.

Control flow: `main` initializes a ring with an SQ array, checks `IORING_FEAT_SUBMIT_STABLE`, creates a listening socket using `getaddrinfo`, prepares an accept SQE in slot 0, submits it through the manual SQ array path, connects a client, waits for and validates the accepted socket address, then repeats as needed.

State and persistence behavior: manually mutated SQ tail/array state is the core state under test. Sockets and ring state are cleaned at exit.

Dependencies and integration points: uses `t_io_uring_init_sqarray`, raw `__sys_io_uring_enter`, memory barriers, networking helpers, and public SQE prep.

Risks: direct SQ manipulation bypasses some high-level helper protections. The test is skipped without `IORING_FEAT_SUBMIT_STABLE` because kernel stability guarantees are required for slot reuse.

Test signals: validates that SQE contents remain stable after submission and direct SQ array reuse does not corrupt accept handling.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/accept-reuse.c -->
