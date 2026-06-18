# File Research: sources/virtualization/spdk/module/sock/posix/posix.c

Implements SPDK’s default POSIX socket network backend plus the SSL socket backend. It registers `posix` as the default `spdk_net_impl` and `ssl` as an additional implementation.

Key responsibilities:
- Socket lifecycle: listen, connect, async connect, accept, close.
- Address helpers: local/peer address lookup, interface-name lookup, NUMA lookup via sysfs.
- Runtime socket operations: `recv`, `readv`, `writev`, async write queueing, flush, connectivity checks, IPv4/IPv6 checks.
- Group polling: epoll on Linux, kqueue on FreeBSD, with a `socks_with_data` queue for level-triggered behavior and fairness rotation.
- Receive buffering: optional `spdk_pipe` receive pipe, including resize, drain, and group integration.
- Zerocopy send support when `SO_ZEROCOPY` and `MSG_ZEROCOPY` are available, including ERRQUEUE completion tracking.
- Placement ID support for grouping sockets by CPU/NIC queue via `spdk_sock_map`.
- TLS/SSL support through OpenSSL, including TLS 1.3 PSK session callbacks, optional kTLS, cipher-suite configuration, and SSL read/write wrappers.

Important structures:
- `struct spdk_posix_sock`: wraps `spdk_sock`, fd, recv pipe, zerocopy state, SSL context/object, placement id, async connect context, and group list node.
- `struct spdk_posix_sock_group_impl`: wraps `spdk_sock_group_impl`, epoll/kqueue fd, interrupt handle, receive-ready list, placement id, and pipe group.
- `struct posix_connect_ctx`: preserves async connect state across address candidates and delayed socket options.

Control flow:
- `_posix_sock_connect()` allocates a socket and creates an async connect context even for synchronous connects; synchronous connect repeatedly calls `posix_connect_poller()`.
- `posix_connect_poller()` handles timeout, connect completion, fallback to the next resolved address, deferred SSL setup, deferred recv/send buffer and low-water settings, and delayed group add.
- `_sock_flush()` prepares queued SPDK socket requests, sends with `sendmsg` or `SSL_write`, advances request offsets, moves complete requests to pending, and completes non-zerocopy requests immediately.
- `_sock_check_zcopy()` consumes socket ERRQUEUE messages and completes pending zerocopy requests by kernel notification index.
- `posix_sock_group_impl_poll()` flushes writes on all group sockets, polls epoll/kqueue, marks sockets with data, returns sockets with callbacks, and rotates the ready list for fairness.

Dependencies and integration points:
- Uses shared sock helpers from `spdk_internal/sock_module.h`.
- Uses `spdk_pipe` and `spdk_pipe_group` for receive buffering.
- Uses Linux `errqueue` and zerocopy APIs conditionally.
- Uses OpenSSL for the `ssl` net implementation.
- Registers `g_posix_net_impl` via `SPDK_NET_IMPL_REGISTER_DEFAULT(posix, ...)`.
- Registers `g_ssl_net_impl` via `SPDK_NET_IMPL_REGISTER(ssl, ...)`.

Notes:
- SSL sockets intentionally disable zerocopy.
- Async connect methods return sockets before readiness; many operations first call `posix_connect_poller()` or report `-EAGAIN`/`-ENOTCONN`.
- Interrupt-mode readiness is based on the group fd, but the implementation also preserves ready sockets in an internal queue for level-triggered behavior.
