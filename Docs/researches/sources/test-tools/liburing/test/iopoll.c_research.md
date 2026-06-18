<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/iopoll.c -->
## sources/test-tools/liburing/test/iopoll.c

Purpose: main polled-IO matrix for read/write, SQPOLL fixed files, registered buffers, provided buffers, hybrid polling, defer-taskrun, and CQE polling helpers.

Important APIs/types/functions: `provide_buffers`, `__test_io`, `test_io_uring_cqe_peek`, `test_io_uring_submit_enters`, `test_io`, `probe_buf_select`, `io_uring_prep_readv`, `io_uring_prep_writev`, `io_uring_prep_read_fixed`, `io_uring_prep_write_fixed`, `IORING_SETUP_IOPOLL`, `IORING_SETUP_HYBRID_IOPOLL`, `IOSQE_BUFFER_SELECT`, and `__io_uring_flush_sq`.

Control flow: `main` probes provided-buffer support, creates a test file and aligned buffers, and runs up to 64 combinations over write/read, SQPOLL, fixed buffers, hybrid IOPOLL, provided buffers, and defer-taskrun. It then verifies that `io_uring_submit` enters the kernel to reap IOPOLL completions and that `io_uring_peek_cqe` can drive IOPOLL completion retrieval.

State and persistence behavior: global flags `no_buf_select`, `no_iopoll`, and `no_hybrid` prune unsupported matrix branches. Temporary file and global buffers back all tests.

Dependencies and integration points: depends on O_DIRECT and device/filesystem IOPOLL support, plus buffer selection and defer-taskrun feature probing.

Risks: environment support varies widely. Some paths detect `-EOPNOTSUPP` after submission and disable further IOPOLL checks.

Test signals: pass means polled IO completes across supported buffer/file modes and liburing CQE peek/submit helpers properly enter the kernel.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/iopoll.c -->
