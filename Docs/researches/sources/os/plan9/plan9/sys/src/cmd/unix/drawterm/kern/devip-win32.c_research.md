# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devip-win32.c

Provides the Windows Winsock backend used by `devip.c`.

Key behavior:
- Initializes Winsock with `WSAStartup`.
- Initializes `sysname` from `gethostname`.
- Implements the same `so_*` socket abstraction as the POSIX backend.
- Supports TCP and UDP sockets, connect, bind, listen, accept, send, receive, service lookup, and host lookup.
- Converts Plan 9 IP addresses to IPv4/IPv6 socket addresses.

Notable differences from POSIX:
- Uses `int` for socket address lengths.
- `hostlookup` returns the original host string when resolution fails, rather than returning `nil`.
- Uses Winsock headers and optional MSVC library pragma.

Notable risks:
- Same privileged-bind byte-order issue as POSIX.
- Host lookup is mostly IPv4-oriented in the `gethostbyname` path.
