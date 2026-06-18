# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printdstlist.c

Destination-list printer for copied or kernel-readable lists.

Key behavior:
- Copies the destination-list header through a supplied copy function.
- Filters by name when requested.
- Prints list metadata and each node through `printdstlistnode()`.
- Handles empty lists with a bare semicolon.

Research notes:
- Allocates each variable-size node using its `ipfd_size`.
