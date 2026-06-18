# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/remove_hashnode.c

Hash lookup-table node removal helper.

Key behavior:
- Copies address and mask from the supplied node.
- Calls `SIOCLOOKUPDELNODE`.
- Debug mode prints the address and mask being removed.

Research notes:
- Removal key does not copy family/group fields, unlike `load_hashnode()`.
