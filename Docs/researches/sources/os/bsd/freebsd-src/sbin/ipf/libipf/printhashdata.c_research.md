# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printhashdata.c

Hash lookup-table metadata formatter.

Key behavior:
- Prints save, normal, and debug variants.
- Distinguishes lookup hash tables from group maps.
- Shows role/unit, name/number, size, seed, references, maskset, anonymous/delete state, and debug masks.

Research notes:
- Debug mask output converts mask bit positions with `ntomask()`.
