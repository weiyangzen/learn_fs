# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/getrpcport.c

Read completely: 85 lines.

Implements `getrpcport()`, the old IPv4-only helper that resolves a hostname with `gethostbyname()`, builds a `sockaddr_in`, and calls `pmap_getport()` for the requested program, version, and protocol.

It returns `0` on host lookup failure or no registered port. The implementation mutates `hp->h_length` if it exceeds the destination address length, which is an old-style convenience but surprising because the `hostent` storage is owned by resolver code.
