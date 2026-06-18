# File Research: sources/os/bsd/netbsd-src/sys/kern/sys_pipe.c

## Purpose
Implements high-performance kernel pipes as paired `DTYPE_PIPE` file descriptors backed by pageable kernel virtual buffers, replacing socket-based pipe behavior.

## Main Interfaces
- `pipe_init`: initializes reader/writer pipe pool caches.
- `pipe1`: creates paired read/write file descriptors, pipe structures, shared lock, peer links, and descriptor flags.
- `pipe_read`, `pipe_write`: implement circular-buffer blocking I/O with `PIPE_BUF` atomicity guarantees.
- `pipe_ioctl`, `pipe_poll`, `pipe_kqfilter`, `pipe_stat`, `pipe_close`, `pipe_restart`.
- Buffer/lifecycle helpers: `pipe_create`, `pipespace`, `pipe_free_kmem`, `pipeclose`, `pipelock`, `pipeunlock`, `pipeselwakeup`.

## State And Control Flow
Each endpoint has a `struct pipe`, peer pointer, shared mutex, condition variables, select info, state flags, timestamps, and a circular `pipebuf`. The reader endpoint preallocates normal pipe KVA; write-side buffers are allocated through the peer. Large writes can expand an empty pipe to `BIG_PIPE_SIZE` up to `maxbigpipes`. Reads block on `pipe_rcv`, writes block on `pipe_wcv`, and both use an internal long-term `PIPE_LOCKFL` I/O lock.

## Dependencies And Integration
Uses descriptor allocation, `fileops`, UVM pageable kernel mappings, pool caches, `uiomove`, select/poll/kqueue, async I/O ownership/signals, stat metadata, sysctl pipe counters, and generic close/restart handling.

## Risks And Edge Cases
- Close sets `PIPE_EOF`, wakes peer waiters, waits for busy I/O to drain, and clears remaining kqueue internals directly.
- Nonblocking read has an unlocked fast path using atomic loads to reduce contention for parallel empty-pipe probes.
- `PIPE_RESTART` converts blocked syscalls to `ERESTART` for descriptor revalidation during close.
- Buffer resize/free must maintain `nbigpipe` and `amountpipekva` accounting.
- Poll write readiness references the peer; closed peer cases must avoid stale pointer use.

## Filesystem Relevance
High descriptor/VFS-adjacent relevance. Pipes are non-vnode file objects with read/write/poll/stat/kqueue semantics and are central to Unix file descriptor behavior.
