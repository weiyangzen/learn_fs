# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/ftov.c

This helper converts socket address families to IP version numbers.

`ftov()` returns `6` for `AF_INET6` when compiled with IPv6 support, `4` for `AF_INET`, `0` for `AF_UNSPEC`, and `-1` for unknown values.
