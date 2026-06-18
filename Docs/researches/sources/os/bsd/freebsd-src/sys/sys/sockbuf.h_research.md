# File Research: sources/os/bsd/freebsd-src/sys/sys/sockbuf.h

Socket buffer state and kernel manipulation API.

Key responsibilities:
- Defines socket buffer flags for TLS RX, wait/select/async/upcall/AIO/kqueue state, coalescing, autosizing, TOE, splice, and TLS resync behavior.
- Defines socket buffer shutdown/mark state bits.
- Defines `struct sockbuf`, including readiness state, accounting fields, watermarks, timeout, upcall, AIO queue, and protocol-specific buffer unions.
- Supports classic BSD mbuf-chain buffers, PF_UNIX stream/seqpacket buffers, PF_UNIX datagram buffers, and netlink queues.
- Declares append, drop, flush, reserve, release, wait, accounting, send pointer, control-message, TLS RX accounting, and readiness helpers.
- Provides inline `sbavail()`, `sbused()`, and `sbspace()`.

Important patterns:
- Readiness-facing fields are at the start of `struct sockbuf` and protected by the owning socket's send/receive buffer locks.
- Classic buffers track mbuf chains, record boundaries, send pointers, not-ready sendfile data, and KTLS state.
- UNIX-domain sockets use specialized queue structures instead of only the classic mbuf chain.
- `sbspace()` returns the limiting space from byte high-water and mbuf memory limits.

Research relevance:
- Main buffer accounting and queueing contract for FreeBSD sockets, including sendfile and KTLS interactions.
