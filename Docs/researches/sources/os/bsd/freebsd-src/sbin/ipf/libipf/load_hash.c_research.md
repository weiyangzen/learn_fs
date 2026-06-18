# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/load_hash.c

Hash lookup-table loader/remover.

Key behavior:
- Counts entries and chooses table size from `iph_size` or `n * 2 - 1`.
- Adds a lookup hash table with `SIOCLOOKUPADDTABLE` unless removing.
- Prints verbose hash output by temporarily creating a local table array.
- Loads each hash node with `load_hashnode()`.
- Deletes the table when `OPT_REMOVE` is set.

Research notes:
- Verbose printing converts listed IPv4 addresses/masks with `htonl()` after printing.
