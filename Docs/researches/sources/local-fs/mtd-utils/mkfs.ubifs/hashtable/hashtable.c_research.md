# File Research: sources/local-fs/mtd-utils/mkfs.ubifs/hashtable/hashtable.c

## Purpose
Implements a generic separate-chaining hashtable with prime table sizes, load-factor expansion, caller-provided hash/equality functions, and ownership of key memory.

## Main Entry Points
- `create_hashtable()` chooses the first prime larger than the requested minimum, allocates the bucket table, and records hash/equality callbacks.
- `hash()` mixes the caller's hash output to reduce sensitivity to poor hash functions.
- `hashtable_insert()` inserts a key/value pair and expands when load exceeds `0.65`.
- `hashtable_search()` returns the value for a matching key.
- `hashtable_remove()` removes an entry, frees its key, and returns the value.
- `hashtable_count()` and `hashtable_destroy()` expose count and teardown.

## Dependencies
Includes `common.h` for `ARRAY_SIZE`, the public/private hashtable headers, libc allocation/string headers, and `ceil()` from libm.

## Risks and Notes
The table permits duplicate keys; callers must remove first if uniqueness matters. `hashtable_destroy(..., free_values)` always frees keys and optionally frees values. The realloc fallback in `hashtable_expand()` appears to call `memset(newtable[h->tablelength], ...)` instead of taking the address of the first new bucket and sizing in bytes, which would be unsafe if that rare fallback path executes.
