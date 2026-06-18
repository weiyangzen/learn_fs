# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printpoolfield.c

Tabular field printer shared by pool, hash, and destination-list nodes.

Key behavior:
- Defines `poolfields[]`: address, mask, interface name, packets, bytes, and family.
- Prints selected fields according to object type `IPLT_POOL`, `IPLT_HASH`, or `IPLT_DSTLIST`.
- Handles `all` sentinel `-2`.

Research notes:
- Destination-list packet/byte fields are hardcoded as zero.
