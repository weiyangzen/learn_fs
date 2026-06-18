# File Research: sources/os/bsd/netbsd-src/lib/libc/include/isc/memcluster.h

ISC memory-cluster allocation interface with private libc symbol remapping.

Defines:
- `meminit`, `memget`, `memput`, `memstats`, `memactive` mappings.
- Debug and record modes that pass `__FILE__` and `__LINE__` to specialized allocation functions.

Declares normal, debug, and record allocation/free functions plus stats and activity checks.
