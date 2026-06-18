# File Research: sources/os/bsd/dragonflybsd/sys/kern/sys_generic.c

## Summary
Implements generic descriptor-based I/O syscalls and compatibility plumbing: `read`, `write`, vectored and positioned variants, `ioctl`, mapped ioctl translation, `select`, `pselect`, `poll`, `ppoll`, OpenBSD poll compatibility, and a helper to wait on sockets through a temporary kqueue.

## Main Responsibilities
- Builds `uio`/`iovec` structures for scalar, vectored, positioned read and write syscalls.
- Holds and drops file references with access checks, then dispatches through `fo_read()` and `fo_write()`.
- Implements `mapped_ioctl()` including command translation maps, stack-vs-heap ioctl buffers, `FIONBIO`, `FIOASYNC`, and copyin/copyout handling.
- Provides registration and unregistration for mapped ioctl handler ranges.
- Implements `select` and `pselect` by translating fd sets into transient kqueue events and copying results back into fd sets.
- Implements `poll` and `ppoll` by translating `pollfd` entries into kqueue events with per-call serial/index tagging.
- Provides `socket_wait()` by temporarily wrapping a referenced socket in a file object and private kqueue.

## Important Behavior
`kern_preadv()` and `kern_pwritev()` reject explicit offsets for non-vnode file types with `ESPIPE`. The common read/write helpers return successful byte counts for partial transfers interrupted by restart, interrupt, or would-block errors. Non-socket `EPIPE` writes signal `SIGPIPE`; sockets handle their own signal semantics.

`mapped_ioctl()` honors optional emulation maps before interpreting IOC direction and length bits. It uses an inline 128-byte stack buffer for small ioctl payloads and heap allocation for larger payloads. `FIONCLEX` and `FIOCLEX` are handled at the descriptor layer before file operation dispatch.

`select`/`poll` are old-API frontends over kqueue. The implementation tags generated events with `lwp_kqueue_serial` so stale events can be filtered or deleted. Unsupported read/write filter errors are often swallowed to match old `select`/`poll` behavior, while bad descriptors propagate as `EBADF` or `POLLNVAL`.

## Dependencies and Integration
This file is tightly coupled to the file descriptor layer (`holdfp`, `dropfp`, descriptor flags), file operation vectors, kqueue, signal masking, ktrace, and socket file operations. It is the generic syscall bridge used by vnode, pipe, socket, device, and message-queue file types.

## Filesystem/Storage Relevance
All regular file and vnode read/write syscalls flow through this layer before reaching filesystem-specific `fo_read`/`fo_write` implementations. Ioctl handling also carries block device, filesystem, terminal, and network control operations.

## Risks
The select/poll emulation depends on careful stale-event cleanup to avoid livelock. `mapped_ioctl()` must keep command length/direction, translation maps, and user copies synchronized or it can expose ABI incompatibilities. The simple `sys_read()` and `sys_write()` negative-size checks assign `EINVAL` but do not return immediately before rebuilding the `uio`, so correctness depends on later paths and unsigned syscall argument conventions.
