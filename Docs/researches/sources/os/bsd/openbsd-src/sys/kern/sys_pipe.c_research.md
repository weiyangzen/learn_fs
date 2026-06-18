# File Research: sources/os/bsd/openbsd-src/sys/kern/sys_pipe.c

Implements OpenBSD anonymous pipes as a dedicated `DTYPE_PIPE` file type rather than socket-backed pipes. It provides pipe creation syscalls, file operations, kqueue filters, async notification, blocking/nonblocking read-write semantics, and pipe-pair lifetime management.

Major structures and globals:
- `struct pipe_pair`: two peer `struct pipe` objects plus one shared `rwlock`.
- `pipeops`: `read`, `write`, `ioctl`, `kqfilter`, `stat`, and `close` handlers for pipe files.
- `pipe_pair_pool`: pool allocator for pipe pairs.
- `nbigpipe`, `amountpipekva`: accounting for expanded pipe buffers and pageable kernel virtual memory.

Creation path:
- `sys_pipe()` and `sys_pipe2()` both call `dopipe()`.
- `sys_pipe2()` accepts only `O_CLOEXEC`, `O_CLOFORK`, and `FNONBLOCK`.
- `dopipe()` allocates a pipe pair, two file structures, two file descriptors, installs descriptor close flags, copies the descriptor pair to userland, and unwinds descriptors and pipe buffers on partial failure.

Buffer and lifetime behavior:
- Each pipe side owns a pageable circular buffer initialized to `PIPE_SIZE`.
- Large writes may grow an empty normal pipe to `BIG_PIPE_SIZE`, limited by `LIMITBIGPIPES`.
- `pipe_destroy()` marks EOF, wakes peer waiters, waits for active I/O via `pipe_busy`, disconnects the peer, frees buffers, and destroys the pair when both sides are gone.
- `pipe_rundown()` coordinates close-time waiters with in-flight read/write paths.

I/O behavior:
- `pipe_read()` drains the read pipe buffer with wraparound handling, resets indices when empty, sleeps on empty pipes, returns EOF on closed peers, and wakes blocked writers once enough space is available.
- `pipe_write()` writes into the peer pipe, preserves atomicity for writes up to `PIPE_BUF`, supports wraparound copies, blocks or returns `EAGAIN` when full, and returns `EPIPE` when the read side is gone.
- Both paths drop the pipe lock around `uiomove()` and use an internal `PIPE_LOCK` I/O lock to serialize buffer mutations.

Notifications and metadata:
- `pipe_ioctl()` supports async mode, `FIONREAD`, and signal-owner ioctls.
- `pipe_stat()` reports FIFO mode, buffer size, buffered byte count, block count, timestamps, and file credential uid/gid.
- kqueue filters implement read readiness, write readiness, poll hangup behavior, and except-filter behavior for poll-style users.

Filesystem/storage relevance:
- Not a filesystem implementation, but directly relevant to VFS/file-descriptor semantics: it defines OpenBSD pipe file operations, `stat(2)` behavior for pipes, descriptor allocation, readiness notification, and close races for a non-vnode kernel file type.
