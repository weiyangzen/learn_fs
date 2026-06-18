# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printpool.c

Pool lookup-table printer for copied/kernel-readable pools.

Key behavior:
- Copies the pool header, filters by name, and prints metadata.
- Copies the node list into local allocated nodes before printing.
- Prints nodes with `printpoolnode()` and frees local copies.

Research notes:
- Does not check allocation/copy failures robustly inside the node-copy loop.
