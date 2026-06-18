# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printdstl_live.c

Live kernel destination-list printer.

Key behavior:
- Filters by name when requested.
- Prints destination-list metadata unless field output is requested.
- Uses `SIOCLOOKUPITER` with `IPLT_DSTLIST` to iterate nodes.
- Deletes the iterator token with `SIOCIPFDELTOK`.

Research notes:
- Allocates fixed extra 64 bytes for variable-sized destination nodes.
