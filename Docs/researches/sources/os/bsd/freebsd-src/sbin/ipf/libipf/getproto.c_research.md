# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/getproto.c

This helper resolves a protocol token.

Numeric strings return `atoi(name)`. The special name `ip` returns `0`. Other names are resolved with `getprotobyname()` and return the protocol number, or `-1` if unknown.
