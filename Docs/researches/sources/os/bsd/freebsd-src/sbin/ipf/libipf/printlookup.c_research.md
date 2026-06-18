# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printlookup.c

Lookup-reference printer for rule addresses.

Key behavior:
- Prints lookup type prefixes for pool, hash, and destination list.
- Prints numeric lookup IDs or name offsets into the rule name buffer.

Research notes:
- Unknown lookup types are printed as `lookup(hex)=`.
