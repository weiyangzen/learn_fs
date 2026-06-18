# File Research: sources/os/bsd/netbsd-src/lib/libc/inet/inet_netof.c

Implements legacy `inet_netof`.

Behavior:
- Converts IPv4 address to host byte order.
- Returns classful network number for class A, B, or C using class masks and shifts.

Compatibility API for pre-CIDR IPv4 code.
