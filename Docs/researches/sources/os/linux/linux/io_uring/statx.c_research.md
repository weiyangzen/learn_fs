# File Research: sources/os/linux/linux/io_uring/statx.c

io_uring statx operation implementation.

Key responsibilities:
- Prepares statx SQEs by capturing dfd, mask, flags, output buffer, and delayed pathname.
- Rejects fixed-file mode and unused SQE fields.
- Forces async execution.
- Executes `do_statx()` and completes with the VFS return code.
- Cleans delayed pathname state.

Important invariants:
- Pathname lifetime is managed by `REQ_F_NEED_CLEANUP` and `io_statx_cleanup()`.
- Issue path expects blocking context and warns on nonblocking issue.
