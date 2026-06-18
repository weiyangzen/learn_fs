# sources/test-tools/liburing/test/unlink.c

Purpose: tests io_uring unlink and rmdir behavior, including successful file unlink, invalid path handling, bad user pointer handling, and directory removal through `AT_REMOVEDIR`.

Important APIs/types/functions: `test_rmdir`, `test_unlink_badaddr`, `test_unlink`, `stat_file`, `io_uring_prep_unlink`, `mkstemp`, `mkdir`, `stat`, `io_uring_queue_init`, `io_uring_submit`, and `io_uring_wait_cqe`.

Control flow: main creates a ring and temporary file, verifies it exists, unlinks it through io_uring, and requires later `stat` to return `ENOENT`. It then queues unlink for a guaranteed missing path and expects `-ENOENT`, queues unlink with address `0x1234` and expects `-EFAULT`, and finally creates/removes a temporary directory with `AT_REMOVEDIR`, verifying it is gone.

State/persistence behavior: creates and removes one temporary file and one temporary directory named with the process id. Error paths attempt cleanup with `unlink`.

Dependencies/integration: exercises VFS unlink/rmdir paths through io_uring and user pointer validation.

Risks/test signals: skips only by returning success when unlink opcode is unsupported (`-EBADF` or `-EINVAL` on the first real unlink). Failures are wrong CQE result codes or filesystem objects remaining after reported success.
