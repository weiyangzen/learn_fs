<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/fsync.c -->
## sources/test-tools/liburing/test/fsync.c

Purpose: validates io_uring fsync, drained fsync ordering, and sync-file-range support.

Important APIs/types/functions: `test_single_fsync`, `test_barrier_fsync`, `test_sync_file_range`, `io_uring_prep_fsync`, `io_uring_prep_writev`, `IOSQE_IO_DRAIN`, `IORING_FSYNC_DATASYNC`, and `io_uring_prep_sync_file_range`.

Control flow: `main` creates a ring, submits a single fsync on a temp file, then submits four writes plus a drained datasync fsync and verifies write CQEs precede fsync unless drain is unsupported. Finally it creates a small file and submits `sync_file_range`.

State and persistence behavior: temporary files are unlinked after opening or after creation. Iovec write buffers are allocated per barrier test and freed afterward.

Dependencies and integration points: exercises file writeback, drain ordering, fsync flags, and sync-file-range opcode.

Risks: older kernels may report `-EINVAL` for drain, which the barrier loop tolerates by breaking. Some error paths leak fd/buffers.

Test signals: pass means fsync operations complete and drained fsync is not observed before prior writes.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/fsync.c -->
