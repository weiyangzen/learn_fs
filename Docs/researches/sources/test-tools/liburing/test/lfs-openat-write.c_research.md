# sources/test-tools/liburing/test/lfs-openat-write.c

Purpose: verifies that an `IORING_OP_OPENAT` result can be used for a large-file write beyond 4 GiB when `O_LARGEFILE` is used.

Important APIs/types/functions: `io_uring_queue_init`, `io_uring_prep_openat`, `io_uring_prep_write`, `io_uring_submit`, `io_uring_wait_cqe`, `open`, `unlink`, `O_LARGEFILE`, and `T_EXIT_SKIP`.

Control flow: `main()` opens `/tmp` as a directory, initializes a small ring, and calls `test_open_write()`. That submits openat for `io_uring_openat_write_test1`, extracts the returned fd from the CQE, and calls `do_write()` at offset `1ULL << 32`.

State and persistence behavior: creates and removes one temporary file under `/tmp`. Persistent test signal is whether the filesystem accepts sparse large-file writes; the code does not inspect file contents afterward.

Dependencies and integration points: depends on large-file-capable filesystem semantics, liburing open/write preparation helpers, and `helpers.h` exit constants. An extra CLI argument skips execution.

Risks and test signals: failure indicates openat completion errors, write submission/CQE errors, or inability to write at a large offset. The opened fd is not explicitly closed in `test_open_write()`, so process exit performs cleanup.
