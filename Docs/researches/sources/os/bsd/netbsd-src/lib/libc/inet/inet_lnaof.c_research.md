# File Research: sources/os/bsd/netbsd-src/lib/libc/inet/inet_lnaof.c

Implements legacy `inet_lnaof`.

Behavior:
- Converts IPv4 address to host byte order.
- Returns the local host-address portion using class A/B/C masks.
- Uses `IN_CLASSA`, `IN_CLASSB`, and class host masks.

This is classful IPv4 compatibility logic.
