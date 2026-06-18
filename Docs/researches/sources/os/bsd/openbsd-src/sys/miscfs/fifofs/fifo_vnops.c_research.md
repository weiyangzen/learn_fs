# File Research: sources/os/bsd/openbsd-src/sys/miscfs/fifofs/fifo_vnops.c

Purpose: Implements named pipe vnode operations using a connected pair of Unix-domain stream sockets.

Key behavior:
- `struct fifoinfo` stores read socket, write socket, reader count, and writer count in the vnode.
- `fifo_open()` lazily creates connected sockets, adjusts socket send/receive shutdown state, tracks readers/writers, implements blocking open semantics, and returns `ENXIO` for nonblocking writer opens with no reader.
- `fifo_read()` and `fifo_write()` temporarily unlock the vnode and call `soreceive()`/`sosend()`.
- `fifo_close()` decrements reader/writer counts, applies `socantsendmore()`/`socantrcvmore()`, marks reader socket disconnected for hangup reporting, and destroys sockets when both sides are gone.
- `fifo_reclaim()` force-closes sockets and clears vnode FIFO state.
- `fifo_ioctl()` forwards operations to the relevant socket side through a temporary file object.
- `fifo_pathconf()` reports FIFO-specific POSIX constants; advisory locks are unsupported.
- `fifo_kqfilter()` attaches read, write, and poll exception filters to socket buffer klists.
- Filter callbacks report EOF/HUP/readability/writability from socket buffer state and implement knote modify/process locking.

Filesystem relevance:
- Provides POSIX FIFO semantics on top of socket buffering and kqueue readiness.
- Interacts with generic vnode fileops via `fifo_vops`.
