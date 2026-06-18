# File Research: sources/teaching/minix/minix/servers/vfs/read.c

Implements read path, shared read/write execution, getdents, pipe I/O, and block-special-file locking helpers.

Key behavior:
- `do_read` validates reserved `cum_io` input and delegates to `do_read_write_peek`.
- `actual_read_write_peek` locks the filp/vnode for read or write, checks access mode, handles zero-length I/O, and calls `read_write`.
- `read_write` dispatches by vnode type:
  - FIFOs use `rw_pipe`.
  - Character devices use asynchronous `cdev_io`.
  - Socket devices use `sdev_readwrite`.
  - Block devices serialize with `lock_bsf` and call `req_breadwrite` or `req_bpeek` through the owning block FS endpoint.
  - Regular files and directories call `req_readwrite` or `req_peek`, honoring `O_APPEND`.
- Writes update cached vnode size for regular files and directories when the final position grows.
- `EPIPE` on writes triggers SIGPIPE unless `O_NOSIGPIPE` is set.
- `do_getdents` validates the fd as readable directory, calls `req_getdents`, and updates filp position.
- `rw_pipe` uses `pipe_check`, suspends when necessary, performs mapped PipeFS `req_readwrite`, updates the pipe's cached size, and handles partial blocking writes.

Block special file lock:
- `lock_bsf` uses `mutex_trylock`; if busy, it suspends the worker while waiting.
- `unlock_bsf` and `check_bsf_lock` provide unlock and shutdown verification.

Notable implementation details:
- Character device I/O may return `SUSPEND`; VFS optimistically advances filp position for async character operations.
- `PEEKING` is rejected for pipes, character devices, and sockets.
