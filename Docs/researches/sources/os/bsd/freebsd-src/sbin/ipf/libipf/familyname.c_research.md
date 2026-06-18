# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/familyname.c

This helper converts address-family constants to display strings.

`familyname()` returns `inet` for `AF_INET`, `inet6` for `AF_INET6` when IPv6 support is compiled, and `unknown` otherwise.
