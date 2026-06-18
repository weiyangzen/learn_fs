# File Research: sources/os/bsd/freebsd-src/sbin/rcorder/hash.c

String-key hash table implementation imported from BSD/Sprite lineage.

Key elements:
- `Hash_InitTable` creates a power-of-two bucket table, defaulting to 16 buckets.
- `Hash_FindEntry` hashes strings with `h = (h << 5) - h + c` and searches the bucket chain by cached hash plus strcmp.
- `Hash_CreateEntry` returns an existing entry or allocates a flexible key-sized entry, rebuilding when entries reach eight times bucket count.
- `Hash_DeleteEntry`, `Hash_DeleteTable`, `Hash_EnumFirst`, and `Hash_EnumNext` provide deletion and full-table enumeration.
- `RebuildTable` doubles bucket count and relinks all entries by cached hash.

Dependencies:
- Uses `sprite.h` for `Boolean`/`ClientData`, `hash.h` for structures/macros, and `ealloc.h` for fatal allocation.

Research notes:
- `Hash_DeleteEntry` aborts on an entry that is not in the expected bucket, treating misuse as programmer error.
- Entries store key text inline through `char name[1]` plus over-allocation.
