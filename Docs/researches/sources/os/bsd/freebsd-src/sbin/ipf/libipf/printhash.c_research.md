# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printhash.c

Hash lookup-table printer for copied/kernel-readable tables.

Key behavior:
- Copies the table header with a supplied copy function.
- Filters by name when requested.
- Prints table metadata and each linked entry through `printhashnode()`.
- Emits an empty semicolon block for empty lists.

Research notes:
- Allocates and copies the bucket table but visible iteration uses `iph_list`; the copied table is not otherwise used.
