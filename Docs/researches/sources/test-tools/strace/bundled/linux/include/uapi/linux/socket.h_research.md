# sources/test-tools/strace/bundled/linux/include/uapi/linux/socket.h

## Purpose

Provides Linux UAPI socket storage and small generic socket-option constants shared by other headers. strace uses it indirectly through address structures such as QRTR, TCP MD5/AO, and generic sockaddr decoding.

## Important APIs, Types, and Dependencies

The header defines `_K_SS_MAXSIZE`, typedef `__kernel_sa_family_t`, and `struct __kernel_sockaddr_storage`, whose anonymous union controls size and pointer alignment. It also exports send/receive buffer lock masks (`SOCK_SNDBUF_LOCK`, `SOCK_RCVBUF_LOCK`, `SOCK_BUF_LOCK_MASK`) and TX rehash option values (`SOCK_TXREHASH_DEFAULT`, `DISABLED`, `ENABLED`).

## Control Flow, State, and Integration

No code flow is present. The ABI role is structural: it gives fixed-size address storage for protocol-specific socket options and generic constants for socket behavior. Kernel state affected by related options is per-socket buffer locking and transmit hash behavior.

## Risks and Test Signals

Risks include assuming libc `sockaddr_storage` is identical, breaking anonymous union layout in C++ consumers, and printing TX rehash values as booleans despite the default sentinel. Test signals include compile/layout checks and strace decoding of socket option values using these constants.
