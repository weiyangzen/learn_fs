# sources/test-tools/liburing/test/statx.c

Purpose: validates io_uring `statx` against the raw `statx` syscall and checks invalid path/buffer error handling.

Important APIs/types/functions: `io_uring_prep_statx`, `struct statx`, raw `syscall(__NR_statx)`, `AT_EMPTY_PATH`, `STATX_ALL`, invalid pointer tests, and helper `t_create_file`.

Control flow: creates or uses a file, submits io_uring statx by path and compares the resulting `struct statx` with a synchronous syscall. It then checks invalid path pointer and invalid output buffer both return `-EFAULT`, and checks fd-based `AT_EMPTY_PATH` statx matches the syscall.

State/persistence behavior: creates `/tmp/.statx` when no path is supplied and unlinks it at the end. Otherwise only metadata is read.

Dependencies/integration: depends on kernel statx syscall and io_uring statx opcode. `-EINVAL` or ENOSYS-compatible paths are treated as unsupported skips.

Risks/test signals: detects metadata mismatch, wrong invalid-pointer errno, unsupported opcode behavior, and cleanup issues for the temporary file.
