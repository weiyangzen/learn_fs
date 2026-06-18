# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/optprintv6.c

IPv6 extension-header match pretty-printer.

Key behavior:
- Compiled only under `USE_INET6`.
- Prints positive `v6hdr` matches from `v6ionames[]`.
- Prints negative `not v6hdrs` matches when mask and bits differ.

Research notes:
- Accepts a `sec` parameter for signature parity but does not use IPv6 security-class data.
