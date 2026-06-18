# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printactiveaddr.c

Active NAT/state address printer.

Key behavior:
- For IPv4, formats through `inet_ntoa()` and caller-supplied format string.
- For IPv6, delegates to `printaddr()` when compiled with `USE_INET6`.

Research notes:
- Silently ignores unknown address versions.
