# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/optvalue.c

IPv4 option lookup helpers.

Key behavior:
- `getoptbyname()` maps option text to its match bit.
- `getoptbyvalue()` maps numeric IP option value to its match bit.

Research notes:
- Returns `(u_32_t)-1` for not found.
