# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/ntomask.c

Prefix-length to address-mask converter.

Key behavior:
- Supports IPv4 and IPv6/unspecified family.
- IPv4 prefixes produce a network-order `u_32_t` mask.
- IPv6 prefixes are delegated to `fill6bits()`.

Research notes:
- Enforces global `use_inet6` restrictions.
