# File Research: sources/os/bsd/freebsd-src/sys/kern/sys_pipe.c

## Purpose
Implements FreeBSD pipe file descriptors, including `pipe2(2)`, anonymous pipe lifecycle, named-pipe integration hooks, pipe `fileops`, poll/kqueue readiness, and high-performance direct-copy pipe I/O.

## Main Elements
- `pipeops`: file operation table for read, write, ioctl, poll, kqueue, stat, close, chmod/chown, kinfo, and descriptor passing.
- `pipeinit()`: creates the UMA zone for `struct pipepair`, initializes pipe inode allocators, and assigns a pseudo device inode.
- `pipe_paircreate()`, `kern_pipe()`, `sys_pipe2()`, `freebsd10_pipe()`: allocate paired endpoints, file descriptors, flags, Capsicum filecaps, and compatibility syscall return behavior.
- `pipe_named_ctor()` / `pipe_dtor()`: construct and tear down pipe-backed named FIFO endpoints.
- `pipespace_new()` / `pipespace()`: allocate or resize pageable pipe KVA, enforce `RLIMIT_PIPEBUF`, reserve privileged pipe buffer space, and preserve circular-buffer contents during resize.
- `pipe_read()` and `pipe_write()`: core blocking/nonblocking pipe I/O with EOF handling, `PIPE_BUF` atomicity, wakeups, resource accounting, timestamps, and MAC checks.
- Direct-write path: `pipe_build_write_buffer()`, `pipe_direct_write()`, `pipe_clone_write_buffer()`, and `pipe_destroy_write_buffer()` pin writer pages and let readers copy from physical pages for larger user writes.
- Notification and metadata: `pipe_ioctl()`, `pipe_poll()`, `pipe_kqfilter()`, `filt_piperead()`, `filt_pipewrite()`, `pipe_stat()`, `pipe_fill_kinfo()`.
- Cleanup: `pipeclose()`, `pipe_free_kmem()`, `pipe_destroy()` coordinate EOF, busy users, peer wakeups, knote teardown, MAC label destruction, credentials, and UMA release.

## Dependencies And Integration
Uses kernel file descriptor allocation, `struct fileops`, UMA, VM pipe maps, resource limits, MAC framework hooks, selinfo/kqueue, signal ownership, vnode operations for named pipes, and syscall wrappers from `sysproto.h`. It is the main bridge between `pipe2(2)`/legacy pipe syscalls and FreeBSD’s generic file descriptor layer.

## Risk Notes
The file is concurrency- and resource-sensitive. Correctness depends on the split mutex plus `PIPE_LOCKFL` protocol because pipe locks are intentionally dropped around `uiomove()`. Direct writes rely on page pinning and must clone buffered data if interrupted. Pipe KVA accounting and resizing are defensive against system-wide exhaustion, but failures must preserve existing buffered data and wake waiters correctly.
