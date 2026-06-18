# File Research: sources/virtualization/guestfs-tools/gnulib/lib/hash.c

Generic chained hash table implementation.

Core design:
- Table has prime-sized bucket array.
- Each bucket head is embedded in the bucket array; collisions use linked overflow entries.
- Overflow entries are recycled through a free list.
- Optional obstack allocation is supported when `USE_OBSTACK` is enabled.

Key APIs implemented:
- Information: bucket count, used buckets, entry count, max bucket length, validation, statistics.
- Lookup and walking: `hash_lookup`, `hash_get_first`, `hash_get_next`, `hash_get_entries`, `hash_do_for_each`.
- Allocation: `hash_initialize`, `hash_clear`, `hash_free`.
- Resizing: `hash_rehash`.
- Mutation: `hash_insert_if_absent`, `hash_insert`, `hash_remove`, deprecated `hash_delete`.

Important implementation details:
- Default tuning grows when used-bucket ratio exceeds `0.8`, with growth factor `1.414`.
- Default shrink is disabled.
- Custom hashers and comparators are optional; defaults use pointer hashing/comparison.
- Pointer hashing rotates address bits to reduce low-bit alignment artifacts.
- Rehash has rollback logic if allocation fails during transfer.
- `NULL` entries are unsupported and abort insertion.

Research relevance: reusable container utility for guestfs tools and common gnulib-derived infrastructure.
