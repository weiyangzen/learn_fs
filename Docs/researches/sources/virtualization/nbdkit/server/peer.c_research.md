# File Research: sources/virtualization/nbdkit/server/peer.c

Purpose: Provides exported helpers for plugins/filters to inspect client peer address, credentials, and security context.

Peer address:
- `nbdkit_peer_name(addr, addrlen)` uses the current thread-local connection and calls `getpeername` on `conn->sockin`.
- Reports errors when no connection is associated with the thread or the socket is closed.

Peer credentials:
- `nbdkit_peer_pid`, `nbdkit_peer_uid`, and `nbdkit_peer_gid` call a shared helper that initializes requested outputs to `-1`.
- Linux/OpenBSD-style `SO_PEERCRED` support reads `struct ucred` or `struct sockpeercred`.
- FreeBSD-style `LOCAL_PEERCRED` support reads `struct xucred`; PID is reported unsupported there.
- Unsupported platforms return an error explaining that peer credential APIs are unavailable.
- Range checks protect conversion to `int64_t`.

Security context:
- With `SO_PEERSEC`, `nbdkit_peer_security_context` queries the label length, allocates a NUL-padded buffer, then reads the label.
- `ENOPROTOOPT` is treated as a non-error absence of security context and logged only as debug.
- Without `SO_PEERSEC`, it reports unsupported platform.
- Returned strings are heap allocated for caller ownership.

Compatibility:
- Like other public helpers, suppresses GCC 12+ nonnull-compare warnings to preserve runtime checks for older plugins.
