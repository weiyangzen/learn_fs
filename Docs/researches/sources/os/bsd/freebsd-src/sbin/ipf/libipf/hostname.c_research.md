# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/hostname.c

This helper converts an IPv4/IPv6 address to a display hostname or numeric string.

For IPv4 it recognizes the special test address `0xfedcba98`, attempts reverse DNS and network-name resolution unless `OPT_NORESOLVE` is set, and falls back to `inet_ntoa()`. For IPv6 builds it uses `inet_ntop()`; without IPv6 support it returns the literal string `IPv6`.

The function uses a static host buffer for resolved names and IPv6 strings.
