# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/v6optvalue.c

IPv6 extension-header lookup helpers.

Key behavior:
- `getv6optbyname()` maps extension-header text to bit.
- `getv6optbyvalue()` maps protocol value to bit.
- Both return `(u_32_t)-1` when not found or IPv6 support is not compiled.

Research notes:
- Entire lookup body is conditional on `USE_INET6`.
