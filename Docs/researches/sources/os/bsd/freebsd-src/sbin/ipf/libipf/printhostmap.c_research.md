# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printhostmap.c

NAT hostmap entry printer.

Key behavior:
- Prints old source/destination mapping to new source/destination.
- Prints use/ref count and optional hash value in verbose mode.

Research notes:
- Uses `printactiveaddress()` for v4/v6 address handling.
