# File Research: sources/os/bsd/netbsd-src/lib/libc/net/getprotobyname.c

Read completely: 56 lines.

This file provides the non-reentrant `getprotobyname` wrapper. It locks `_protoent_mutex`, calls `getprotobyname_r` with the global `_protoent_data`, unlocks, and returns the resulting `protoent`.

Security/reliability notes: locking protects internal global state, but the returned pointer still refers to shared global storage that may be overwritten by later protocol database calls.
