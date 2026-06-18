# sources/test-tools/liburing/test/mkdir.c

Purpose: validates `IORING_OP_MKDIRAT` success and common error paths.

Important APIs/types/functions: `io_uring_prep_mkdirat`, `io_uring_wait_cqes`, `stat`, `unlinkat`, `AT_FDCWD`, `AT_REMOVEDIR`, and `strerror`.

Control flow: submits mkdirat for `io_uring-mkdirat-test`, checks it exists via `stat`, submits again expecting `-EEXIST`, submits a missing-parent path expecting `-ENOENT`, and submits a bogus pointer expecting `-EFAULT`.

State and persistence behavior: creates one temporary directory and removes it with `unlinkat(..., AT_REMOVEDIR)`.

Dependencies and integration points: depends on current working directory permissions, mkdirat opcode support, and liburing completion helpers.

Risks and test signals: `-EBADF` or `-EINVAL` skips unsupported kernels; any unexpected errno or missing directory is a failure.
