# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_hash.c

String hash adapter for Citrus in-memory hash tables.

Key behavior:
- `_citrus_string_hash_func` wraps a C string in a `_region`.
- Uses `_db_hash_std` and reduces modulo caller-provided hash size.

Used by mapper and iconv caches so in-memory cache keys share the same case-folded basic-character hash family.
