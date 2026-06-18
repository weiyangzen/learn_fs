# sources/test-tools/liburing/test/truncate.c

Purpose: validates io_uring file truncation operations, especially large file sizes and invalid opcode usage. It exercises `IORING_OP_FTRUNCATE` through the liburing prep helper and ensures malformed truncate usage fails with `-EINVAL`.

Important APIs/types/functions: `test_truncate`, `test_ftruncate`, `get_file_size`, `io_uring_prep_ftruncate`, raw `io_uring_prep_rw(IORING_OP_FTRUNCATE, ...)`, `mkostemp`, `fstat`, `ioctl(BLKGETSIZE64)`, and size constants for 2 GiB, 1 GiB, and 512 MiB.

Control flow: main creates a one-entry ring and a temporary file, then ftruncates it through io_uring to 2 GiB, 1 GiB, and 512 MiB. After each completion it reads back the size via `fstat` or block-device ioctl semantics and checks equality. It then queues a deliberately invalid raw truncate form with a bogus pointer argument and expects `-EINVAL`.

State/persistence behavior: modifies a temporary file size and unlinks it before exit. Large sparse sizes are used, so disk data allocation should be minimal.

Dependencies/integration: depends on large-file support, filesystem truncate behavior, liburing ftruncate prep, and stat/ioctl size queries.

Risks/test signals: skips when ftruncate returns unsupported errors on the first size. Failures include unexpected CQE results, wrong file size, submit/wait errors, or invalid raw truncate not returning `-EINVAL`.
