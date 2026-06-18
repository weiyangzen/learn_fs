# File Research: sources/os/linux/linux/fs/mbcache.c

## Purpose
`mbcache.c` implements a small reusable key/value cache used by ext2/ext4 for extended attribute block/value deduplication. Keys are not unique, but key/value pairs are expected to identify entries uniquely.

## Main Responsibilities
- Creates and destroys `struct mb_cache` instances with fixed-size hash tables.
- Creates cache entries and rejects duplicate key/value pairs.
- Finds reusable entries by key and iterates through hash-chain matches.
- Gets entries by key/value.
- Deletes an entry if unused, or returns a referenced busy entry.
- Touches entries to bias shrinker retention.
- Implements shrinker callbacks and background shrink work.
- Owns the slab cache for `struct mb_cache_entry`.

## Key Data Structures
- `struct mb_cache`: hash buckets, bucket bit count, max entry threshold, LRU-like list, entry count, shrinker, and shrink work.
- `struct mb_cache_entry`: referenced through public mbcache headers; stores key, value, flags, refcount, hash linkage, and list linkage.
- Hash buckets use `hlist_bl_head` bit locks; the global list uses `c_list_lock`.

## Control Flow
`mb_cache_entry_create()` schedules background shrink when entry count exceeds the max and performs synchronous shrink at twice the max. It allocates an entry with refcount 2, checks for duplicate key/value under the bucket lock, inserts into the hash, inserts into the global list, increments count, and drops the temporary setup reference.

Find operations use `__entry_find()`, which scans a bucket for reusable entries and grabs references with `atomic_inc_not_zero()`. `mb_cache_entry_find_next()` drops the old entry reference as it advances.

`mb_cache_entry_delete_or_get()` gets a matching entry, then atomically changes refcount from 2 to 0 to delete only when the hash reference plus caller reference are the only refs. If busy, it returns the referenced entry to the caller.

`mb_cache_shrink()` scans the list, clears referenced bits and moves recently referenced or busy entries to the tail, and frees unused entries by dropping their hash ref and removing them from both list and hash.

## Integration Points
- Exported to filesystem code through `linux/mbcache.h`.
- Shrinker integrates with kernel memory reclaim.
- Module init/exit creates and destroys the entry slab.

## Concurrency and Lifetime Notes
- Bucket bit locks protect hash chains.
- `c_list_lock` protects the global list and entry count.
- Refcount transitions guard deletion races between lookup and delete.
- `mb_cache_destroy()` assumes no external users can reach the cache except the shrinker; it cancels work and frees the shrinker before walking entries without locks.

## Risks and Edge Cases
- The two-lock design intentionally avoids nesting list lock inside bucket bit locks in the create path, which matters for RT.
- `mb_cache_entry_wait_unused()` waits until refcount is at most 2, meaning only the hash/setup-style references remain.
- Shrink retention is approximate; touched entries get one pass of protection via `MBE_REFERENCED_B`.
