# File Research: sources/os/bsd/dragonflybsd/sys/kern/sys_pipe.c

## Summary
Implements DragonFly BSD's high-performance full-duplex pipe file type. It replaces socket-backed pipes with two VM-backed circular buffers, one for each direction, and supports `pipe`, `pipe2`, read/write, ioctl, stat, close, shutdown, kqueue filters, SIGIO, and per-CPU structure caching.

## Main Responsibilities
- Creates pipe descriptor pairs in `kern_pipe()`, honoring `O_CLOEXEC`, `O_CLOFORK`, and `O_NONBLOCK` for `pipe2`.
- Allocates and resizes pageable VM-backed pipe buffers in `pipespace()`.
- Caches pipe structures per CPU to reduce allocation churn.
- Serializes simultaneous reads and writes with per-buffer LWKT tokens and `pipe_start_uio()` / `pipe_end_uio()`.
- Implements circular-buffer read/write paths with nonblocking behavior, atomic writes up to `PIPE_BUF`, busy-delay optimization, and wait/wakeup handling.
- Provides socket-compatible ioctls for async I/O, byte count, and owner process/group.
- Implements close and shutdown state transitions for half-closed and fully closed pipes.
- Implements kqueue read/write filters with EOF, HUP, and capacity/data reporting.

## Important Behavior
Each `struct pipe` contains `bufferA` and `bufferB`. A file pointer stores the pipe address with the low bit selecting which side it represents. Reads consume from the selected side's buffer; writes append to the peer-visible buffer.

The read and write paths use monotonic `rindex`/`windex` counters masked by buffer size for offsets. Memory fences protect ordering between data copies and index publication. Writers cap a single transfer to half the buffer to improve reader wakeup behavior, and writes whose original size is at most `PIPE_BUF` do not proceed unless enough space exists for the whole write.

On SMP systems with timestamp counter support, both readers and writers can busy-wait for a few microseconds before sleeping, reducing wakeup/IPI overhead for synchronous pipe traffic. Large transfers periodically yield and check for pending signals.

## Dependencies and Integration
This file integrates with file descriptors, `struct fileops`, kqueue, signal ownership, VM objects, kernel maps, per-CPU globaldata, sysctls, and scheduler sleep/wakeup primitives. It returns `S_IFIFO` stat data with anonymous inode numbers derived per CPU.

## Filesystem/Storage Relevance
Pipes are a core file type used by the VFS/file-descriptor layer even though they are not filesystem-backed. Their read/write and readiness behavior must match regular descriptor semantics expected by shells, daemons, and event loops.

## Risks
The implementation has many concurrency-sensitive state bits (`PIPE_WANTR`, `PIPE_WANTW`, `PIPE_REOF`, `PIPE_WEOF`, `PIPE_CLOSED`, `PIPE_ASYNC`) and relies on token ordering plus atomic operations. Buffer VM allocation and per-CPU cache teardown can contend with `kernel_map` under mass process exit. Kqueue filter paths intentionally avoid locking and rely on knote processing plus later wakeups to tolerate races.
