# File Research: sources/os/linux/linux/fs/pipe.c

## Purpose
Implements Linux anonymous pipes, FIFOs, pipefs pseudo-filesystem support, pipe buffer accounting, pipe resizing, and pipe-specific syscall/fcntl/ioctl behavior. This file is the core VFS implementation behind `pipe()`, `pipe2()`, named FIFO open/read/write semantics, and kernel pipe buffers used by splice-style paths.

## Main Responsibilities
- Maintains `struct pipe_inode_info` lifetime, wait queues, reader/writer counters, ring buffers, temporary page caches, and user page accounting.
- Implements anonymous pipe reads/writes via `anon_pipe_read()` and `anon_pipe_write()`, with FIFO wrappers that update access/write metadata.
- Provides pipe buffer operations: anonymous release, steal, get, and generic exported buffer helpers.
- Creates pipe file pairs with `create_pipe_files()`, `__do_pipe_flags()`, `do_pipe_flags()`, and syscall wrappers for `pipe`/`pipe2`.
- Implements FIFO open behavior in `fifo_open()`, including blocking/nonblocking POSIX semantics for read-only, write-only, and read-write opens.
- Provides `FIONREAD`, watch queue ioctls, poll, fasync, and fcntl pipe-size controls.
- Registers the internal `pipefs` pseudo filesystem and sysctls under `fs`.

## Key Interfaces
- Exported helpers: `pipe_lock`, `pipe_unlock`, `generic_pipe_buf_try_steal`, `generic_pipe_buf_get`, `generic_pipe_buf_release`, `alloc_pipe_info`, `free_pipe_info`, `round_pipe_size`, `pipe_resize_ring`, `get_pipe_info`, `pipe_fcntl`, `do_pipe_flags`.
- File operation tables: `pipefifo_fops` for FIFOs and `pipeanon_fops` for anonymous pipes.
- Sysctls: `pipe-max-size`, `pipe-user-pages-hard`, `pipe-user-pages-soft`.

## Control Flow and Data Handling
Pipe reads acquire `pipe->mutex`, handle watch-queue loss notifications, consume `pipe_buffer` entries from tail to head, release pages when buffers empty, and wake writers/readers after unlock as needed. Writes preallocate pages outside the mutex for large writes, merge into the previous mergeable buffer when possible, allocate page-backed buffers, publish them by advancing `head`, and wake readers or writers according to empty/full transitions.

The ring uses unmasked monotonically wrapping `head`/`tail` indices, masking only at dereference. Pipe resizing allocates a new power-of-two buffer array, copies live buffers in ring order, resets `tail` to zero and `head` to occupancy, then adjusts accounting and wakeups.

## Dependencies and Integration
Depends heavily on VFS file/inode APIs, wait queues, page allocation/accounting, memcg charging, `iov_iter`, fasync, poll/epoll flags, pseudo fs registration, sysctl, and optional `CONFIG_WATCH_QUEUE`. It is also coupled to splice through pipe buffer operations and `iter_file_splice_write`.

## Concurrency and Lifetime Notes
The primary synchronization object is `pipe->mutex`; watch queues additionally use `rd_wait.lock` because notifications may arrive without holding the mutex. Reader/writer counters govern EOF, `SIGPIPE`, `EPIPE`, wakeups, and FIFO open blocking. `put_pipe_info()` frees the pipe when the last file reference disappears. Temporary page caching in `tmp_page[]` reduces allocator churn but must preserve page refcount and memcg semantics.

## Risks and Review Hotspots
- Wakeup logic is delicate: missed or excessive wakeups can deadlock jobserver-like users or break epoll behavior.
- `pipe_resize_ring()` must preserve buffer order and not shrink below current occupancy.
- Watch queue pipes are intentionally restricted for writes/splice and resizing; violating that can break notification invariants.
- Page stealing and release paths must maintain refcounts, locking, and memcg charging.
- FIFO open paths rely on reader/writer counters and partner wakeups; small changes can alter POSIX visible blocking behavior.
