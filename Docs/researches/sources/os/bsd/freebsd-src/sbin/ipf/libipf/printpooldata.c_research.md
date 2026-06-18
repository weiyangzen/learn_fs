# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printpooldata.c

Pool metadata formatter.

Key behavior:
- Prints save, normal, and debug representations of a pool table.
- Shows role/unit, name/number, anonymous/delete state, references, hits, and node-list pointer.

Research notes:
- Save output uses `pool .../tree` syntax.
