# sources/test-tools/liburing/test/symlink.c

Purpose: validates io_uring `symlinkat` operation success and common error cases.

Important APIs/types/functions: `io_uring_prep_symlinkat`, `io_uring_wait_cqes`, `readlink`, `unlinkat`, `AT_FDCWD`, and invalid user pointers.

Control flow: creates a symlink from a fixed target string to a fixed link name through io_uring, verifies link contents with `readlink`, then checks duplicate link returns `-EEXIST`, missing parent path returns `-ENOENT`, bad newname pointer returns `-EFAULT`, and bad oldname pointer returns `-EFAULT`.

State/persistence behavior: creates one symlink in the current directory and removes it on exit/error. No target file is required because symlink contents are textual.

Dependencies/integration: depends on symlinkat opcode support and filesystem symlink support. `-EBADF` or `-EINVAL` on initial operation is treated as unsupported.

Risks/test signals: detects wrong errno mapping, bad symlink contents, missing cleanup, or unsupported opcode behavior.
