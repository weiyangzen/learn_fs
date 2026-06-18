# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devip-posix.c

Provides the POSIX socket backend used by `devip.c`.

Key behavior:
- Chooses `AF_INET` for v4-mapped Plan 9 addresses and `AF_INET6` otherwise.
- Implements socket creation for TCP and UDP.
- Sets `TCP_NODELAY` on sockets.
- Implements connect, bind, listen, accept, send, receive, getsockname, service lookup, and host lookup.
- Converts between Plan 9 16-byte IP addresses and POSIX IPv4/IPv6 socket structures.
- Initializes `sysname` from `gethostname`.

Important interfaces:
- Implements all `so_*` functions declared in `devip.h`.
- `hostlookup` uses `gethostbyname` first and falls back to `getaddrinfo`.

Notable risks:
- The privileged-bind path writes port `i` directly into sockaddr fields without `hnputs`, unlike the normal bind path.
- `so_gethostbyname` only formats IPv4 hostent results.
