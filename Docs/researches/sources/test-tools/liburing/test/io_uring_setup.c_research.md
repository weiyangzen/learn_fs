<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/io_uring_setup.c -->
## sources/test-tools/liburing/test/io_uring_setup.c

Purpose: low-level unit tests for the `io_uring_setup` syscall ABI.

Important APIs/types/functions: `try_io_uring_setup`, raw `io_uring_setup`, `struct io_uring_params`, `IORING_SETUP_SQ_AFF`, `IORING_SETUP_SQPOLL`, `get_nprocs_conf`, and `read` on ring fd.

Control flow: the test checks expected setup failures for zero entries, null params, nonzero reserved fields, invalid flags, SQ_AFF without SQPOLL, and SQPOLL CPU affinity outside the configured CPU range. It then creates a valid ring fd and verifies normal `read` from that fd fails.

State and persistence behavior: only transient ring fds are created; valid fds are closed after unexpected success or left to process exit in the final check.

Dependencies and integration points: directly validates kernel setup argument checking and ring fd file operations.

Risks: `-EPERM` for privileged setup cases is tolerated for non-root. The helper compares raw negative syscall-style returns.

Test signals: pass means setup rejects malformed params and ring fds are not readable as normal files.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/io_uring_setup.c -->
