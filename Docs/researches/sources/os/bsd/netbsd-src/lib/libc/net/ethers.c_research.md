# File Research: sources/os/bsd/netbsd-src/lib/libc/net/ethers.c

Read completely: 221 lines.

This file implements Sun-style `/etc/ethers` helpers: `ether_ntoa`, `ether_aton`, `ether_ntohost`, `ether_hostton`, and `ether_line`, with weak aliases for libc namespace use.

`ether_ntoa` formats an Ethernet address into a static string; `ether_aton` parses colon-separated hex bytes into a static `struct ether_addr`; `ether_line` parses one ethers database line into address and hostname; host/address lookup routines scan `_PATH_ETHERS` using `fparseln`, with optional YP lookups when compiled with `YP`.

Security/reliability notes: `ether_ntoa` and `ether_aton` return static storage and are not thread-safe. Parsing with `%x` casts to `u_char` and does not reject byte values above `0xff`, so callers should not treat it as strict validation.
