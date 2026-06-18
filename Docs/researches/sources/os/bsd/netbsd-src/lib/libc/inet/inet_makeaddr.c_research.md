# File Research: sources/os/bsd/netbsd-src/lib/libc/inet/inet_makeaddr.c

Implements legacy `inet_makeaddr(net, host)`.

Behavior:
- Builds an IPv4 address from network and host portions using classful thresholds.
- Uses class A/B/C shifts and host masks when `net` fits those classes.
- Otherwise ORs `net | host`.
- Returns network-byte-order `struct in_addr`.

Compatibility helper for older classful networking APIs.
