# sources/user-network-fs/samba/source4/lib/socket/socket_ip.c

## Purpose

`socket_ip.c` implements IPv4 and IPv6 `socket_ops` backends for source4 sockets. It wraps POSIX `socket`, `bind`, `connect`, `listen`, `accept`, `recv`, `send`, `recvfrom`, `sendto`, address reporting, options, and pending-byte queries behind NTSTATUS-returning Samba APIs.

## Important APIs, Types, and Functions

Exports are `socket_ipv4_ops()` and, when IPv6 is available, `socket_ipv6_ops()`. Important helpers include `ipv4_init()`, `ipv4_connect()`, `ipv4_listen()`, `ipv4_accept()`, `ipv4_recvfrom()`, `ipv4_sendto()`, shared `ip_connect_complete()`, `ip_recv()`, `ip_send()`, `ip_pending()`, `ip_close()`, and IPv6 equivalents such as `interpret_addr6()`, `fix_scope_id()`, `ipv6_tcp_connect()`, `ipv6_listen()`, and `ipv6_tcp_accept()`.

## Control Flow

Initialization maps Samba stream/datagram types to `SOCK_STREAM` or `SOCK_DGRAM`, creates an AF_INET or AF_INET6 fd, marks close-on-exec, and records backend name/family. Connect optionally binds a local address, resolves textual numeric addresses, calls `connect()`, then validates completion through `SO_ERROR` and switches to nonblocking mode. Listen sets `SO_REUSEADDR`, binds, calls `listen()` for stream sockets, and marks server-listen state.

## State and Persistence Behavior

The backend stores only fd, backend name, and family in `socket_context`; per-call address objects are talloc-owned by the caller context. Listening and connected states are set in the common context. IPv6 listen forces `IPV6_V6ONLY` before bind.

## Dependencies and Integration Points

The file depends on POSIX networking, Samba address utilities `interpret_addr2()`, `set_socket_options()`, close-on-exec helpers, and NTSTATUS errno mapping. It is selected by `socket_getops_byname("ip"|"ipv4"|"ipv6")` and used by socket tests, stream transports, and SMB connection paths.

## Risks and Edge Cases

Textual address parsing accepts only numeric-style addresses through Samba helpers; unresolved hostnames are not resolved here. IPv4 treats an all-zero parsed server address as bad/unreachable. IPv6 link-local scope parsing depends on `%ifname`. `gethostbyaddr()` can block or fail. Accepted contexts omit `family` initialization in copied fields.

## Test Signals

Current local tests cover IPv4 UDP and TCP loopback. Stronger coverage should include IPv6 loopback, link-local scoped addresses, datagram source address reporting, `FIONREAD` pending behavior, nonblocking connect completion failures, and `IPV6_V6ONLY` binding interactions.
