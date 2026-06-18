# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_db_hash.c

Standard Citrus DB hash function.

Key behavior:
- `_citrus_db_hash_std` iterates a region byte by byte.
- Lowercases bytes through BCS before hashing, making hash values case-insensitive for basic letters.
- Uses a classic nibble-shift hash with high-nibble folding.

The hash is shared by DB builders and readers, so serialized DB lookup depends on this exact function.
