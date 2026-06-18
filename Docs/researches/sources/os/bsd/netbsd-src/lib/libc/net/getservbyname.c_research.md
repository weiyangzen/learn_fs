# File Research: sources/os/bsd/netbsd-src/lib/libc/net/getservbyname.c

Read completely: 56 lines.

This file provides the non-reentrant `getservbyname` wrapper. It locks `_servent_mutex`, calls `getservbyname_r` with global service database state, unlocks, and returns the result.

Important interactions: `getaddrinfo.c` and `getnameinfo.c` use service lookups to map service names and ports for socket address APIs.

Security/reliability notes: returned data is shared global storage and may be overwritten by later non-reentrant service database calls.
