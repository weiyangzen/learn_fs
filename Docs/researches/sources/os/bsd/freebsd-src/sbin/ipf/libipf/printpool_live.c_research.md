# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printpool_live.c

Live kernel pool lookup-table printer.

Key behavior:
- Prints metadata unless field output is requested.
- Iterates pool nodes with `SIOCLOOKUPITER`.
- Prints save, normal, or debug block syntax.
- Deletes the iterator token with `SIOCIPFDELTOK`.

Research notes:
- Only iterates when `pool->ipo_list != NULL`.
