<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/fallocate.c -->
## sources/test-tools/liburing/test/fallocate.c

Purpose: validates io_uring fallocate, linked fallocate+fsync, and file-size-limit error propagation.

Important APIs/types/functions: `test_fallocate`, `test_fallocate_fsync`, `test_fallocate_rlimit`, `io_uring_prep_fallocate`, `io_uring_prep_fsync`, `IOSQE_IO_LINK`, `RLIMIT_FSIZE`, and `SIGXFSZ`.

Control flow: `main` installs a `SIGXFSZ` handler, creates a ring, checks a 128 KiB fallocate updates file size, checks linked fallocate plus fsync both complete successfully, then lowers `RLIMIT_FSIZE` and expects a larger fallocate to fail with `-EFBIG`.

State and persistence behavior: each scenario uses an unlinked `mkstemp` file. `no_fallocate` suppresses dependent checks after unsupported fallocate detection.

Dependencies and integration points: exercises file allocation, linked SQE sequencing, fsync, signal/rlimit interaction, and CQE error mapping.

Risks: mutates process file-size rlimit without restoring it. Unsupported filesystems or kernels return skip via `-EINVAL` or `-EOPNOTSUPP`.

Test signals: pass means fallocate success updates `st_size`, linked fsync is ordered, and rlimit failure is surfaced as `-EFBIG`.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/fallocate.c -->
