# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printhash_live.c

Live kernel hash lookup-table printer.

Key behavior:
- Prints hash metadata unless field output is requested.
- Iterates nodes with `SIOCLOOKUPITER` using `IPLT_HASH`.
- Prints each node with `printhashnode()`.
- Deletes iterator token with `SIOCIPFDELTOK`.

Research notes:
- Reports an iterator-walk error if it exits before the final node.
