# File Research: sources/os/bsd/netbsd-src/lib/libwrap/socket.c

## Summary
Provides socket-specific endpoint discovery and address/name conversion for TCP wrappers request evaluation.

## Main Responsibilities
- Install socket methods into `request_info` via `sock_methods()`.
- Determine client address using `getpeername()` or UDP `recvfrom(..., MSG_PEEK)`.
- Determine server address using `getsockname()`.
- Convert socket addresses to numeric host strings with `getnameinfo(..., NI_NUMERICHOST)`.
- Resolve hostnames with reverse DNS, reject numeric-looking PTR records, and verify reverse names by forward lookup.
- Provide a datagram sink that drains unread UDP messages on cleanup.

## Key Interfaces
- `sock_host(struct request_info *request)`.
- `sock_hostaddr(struct host_info *host)`.
- `sock_hostname(struct host_info *host)`.
- Static `sock_sink(int fd)`.

## Risks
Endpoint storage is static, so results are not reentrant. Hostname trust depends on DNS consistency and can mark names `paranoid` on mismatches or failed verification. UDP peeking leaves payload unread until cleanup. The optional `APPEND_DOT` path can change resolver behavior.
