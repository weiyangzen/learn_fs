# File Research: sources/os/bsd/openbsd-src/sys/sys/socketvar.h

Kernel socket and socket-buffer internal contract.

This header defines `struct sockbuf`, `struct socket`, optional splice state, accept queues, socket state bits, buffer flags, and the lock annotations used throughout OpenBSD socket code. It exposes the kernel socket operation prototypes for fileops, append/drop/flush buffer operations, creation, connect/listen/accept, send/receive, socket options, shutdown, wakeup, locking, syscall helpers, and debug checks.

Inline helpers manage reference taking, splice checks, notification tests, buffer space computation, atomic-send detection, readable/writeable tests, sockbuf accounting, and empty-buffer fixup. The header also declares `sb_max` and `socket_pool`.

Filesystem/storage relevance: important at the descriptor layer. Sockets share file-table, kqueue, ioctl, stat, close, and descriptor-passing paths with VFS objects. UNIX-domain sockets can be filesystem nodes, and socket buffers can carry rights to files.
