# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/hashmap.c

## Role

Small generic chained hashmap with insertion-order iteration.

## Main Flow

- `ext2fs_djb2_hash()` hashes arbitrary byte strings.
- `ext2fs_hashmap_create()` allocates a map, stores hash/free callbacks, and initializes bucket/list heads.
- `ext2fs_hashmap_add()` allocates an entry, links it into a bucket chain, and prepends it to the order list.
- `ext2fs_hashmap_lookup()` compares key length and key bytes.
- `ext2fs_hashmap_iter_in_order()` walks insertion-order list.
- `ext2fs_hashmap_free()` frees entries and optionally payloads via callback.

## Dependencies

Uses `hashmap.h`, libc allocation, and `memcmp`.

## Risks / Notes

- Keys are not copied; callers must keep key storage alive and immutable for the map lifetime.
- Creation overallocates bucket storage using entry size instead of pointer size, wasting memory but not underallocating.
- There is no delete implementation despite a declaration in the header.
