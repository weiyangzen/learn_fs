# File Research: sources/os/linux/linux-stable/fs/mbcache.c

## Summary
Metadata block cache used by ext2/ext4 xattr deduplication. It is a fixed-size hash-backed key/value cache where keys may collide but key/value pairs are expected unique.

## Main APIs
`mb_cache_create()`, `mb_cache_destroy()`, `mb_cache_entry_create()`, `mb_cache_entry_find_first()`, `mb_cache_entry_find_next()`, `mb_cache_entry_get()`, `mb_cache_entry_delete_or_get()`, `mb_cache_entry_touch()`, `mb_cache_entry_wait_unused()`, and `__mb_cache_entry_free()`.

## Behavior
Entries have hash-list membership, LRU-like list membership, refcount, key, value, and reusable/referenced flags. Creation rejects duplicate key/value pairs and initially holds two refs to avoid nesting list lock under hash bucket bit locks. Searches return reusable entries with live refs. Shrinking drops unreferenced entries, giving referenced entries a second chance by clearing the referenced bit and moving them to the tail.

## State and Synchronization
Hash buckets use `hlist_bl` bit locks. Cache list/count use `c_list_lock`. A shrinker and background work item reclaim entries when counts exceed thresholds.

## Dependencies
Kernel shrinker API, slab cache `mb_cache_entry`, workqueues, list/hash primitives, and exported mbcache helpers used by filesystems.

## Risks
`mb_cache_entry_delete_or_get()` relies on exact refcount value `2` to atomically delete an unused hashed entry. Destroy assumes no external users except the shrinker and warns if entries still have unexpected refs.
