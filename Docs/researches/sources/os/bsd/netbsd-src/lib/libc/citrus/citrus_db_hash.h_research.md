# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_db_hash.h

Declares the standard Citrus DB hash function.

Key behavior:
- Exposes `_citrus_db_hash_std(void *, struct _citrus_region *)`.

Used by compiled lookup DBs, ESDB files, pivot DBs, and locale category DBs.
