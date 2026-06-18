# File Research: sources/os/bsd/netbsd-src/lib/libc/net/getprotobynumber.c

Read completely: 57 lines.

This file provides the non-reentrant `getprotobynumber` wrapper. It locks `_protoent_mutex`, calls `getprotobynumber_r` with global protocol database state, unlocks, and returns the result.

Security/reliability notes: returned data uses shared global storage and is overwritten by subsequent non-reentrant protocol database calls.
