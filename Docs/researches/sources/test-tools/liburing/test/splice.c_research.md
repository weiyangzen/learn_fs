# sources/test-tools/liburing/test/splice.c

Purpose: validates io_uring splice and tee operations across file-to-pipe, pipe-to-file, pipe-to-pipe, zero-length operations, invalid offsets, non-pipe tee failures, and registered fixed-file mode.

Important APIs/types/functions: `io_uring_prep_splice`, `IORING_OP_SPLICE`, `IORING_OP_TEE`, `SPLICE_F_FD_IN_FIXED`, `IOSQE_FIXED_FILE`, `io_uring_register_files`, `IORING_FEAT_FAST_POLL`, pipes, temporary files, and random data verification.

Control flow: initializes input/output files, two pipes, and random buffers. It probes splice and tee support by expecting `-EBADF` for invalid fds, runs all positive and negative checks with real fds, registers six fds, remaps context fds to fixed indexes, sets fixed-file flags, and repeats the same splice/tee suite.

State/persistence behavior: temporary files are created then unlinked while open; buffers contain random expected content. Pipe/file offsets and registered file indexes are the main mutable state.

Dependencies/integration: requires fast-poll feature for splice support in this test, filesystem temp files, `/dev/urandom`, pipes, and fixed-file registration.

Risks/test signals: detects data corruption, wrong offset handling, missing invalid-operation errno (`-ESPIPE`/`-EINVAL`), fixed-file splice regressions, and incomplete splice loops.
