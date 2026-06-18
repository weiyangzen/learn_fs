# File Research: sources/os/bsd/netbsd-src/lib/libc/net/getservbyport.c

Thread-safe public wrapper for non-reentrant `getservbyport()`. It locks `_servent_mutex`, calls `getservbyport_r()` using the global `_servent_data.serv` and `_servent_data`, then unlocks and returns the shared `struct servent *`.

This file contains no parsing logic; all storage handling and lookup behavior are in `getservbyport_r.c` and `getservent_r.c`.
