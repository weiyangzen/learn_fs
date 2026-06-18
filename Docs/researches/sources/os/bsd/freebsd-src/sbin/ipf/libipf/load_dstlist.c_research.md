# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/load_dstlist.c

Destination-list table loader/remover for the IPFilter lookup device.

Key behavior:
- Builds an `iplookupop_t` of type `IPLT_DSTLIST`.
- Adds the table unless `OPT_REMOVE` is set.
- In verbose mode, prints the destination list before loading nodes.
- Loads each destination node with `load_dstlistnode()`.
- Deletes the table when `OPT_REMOVE` is set.

Research notes:
- Empty destination-list names are rejected.
