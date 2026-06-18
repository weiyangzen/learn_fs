# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printhost.c

Host address printer.

Key behavior:
- Prints `any` for unknown family or zero address.
- Prints IPv4 with `inet_ntoa()` or IPv6 with `inet_ntop()` when enabled.

Research notes:
- IPv6 path passes the supplied address pointer directly to `inet_ntop()`.
