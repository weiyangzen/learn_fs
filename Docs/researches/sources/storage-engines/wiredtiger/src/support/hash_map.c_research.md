# sources/storage-engines/wiredtiger/src/support/hash_map.c

## Purpose
`hash_map.c` implements a small internal hash map with separately locked buckets. It stores copied key/value blobs in `WT_HASH_MAP_ITEM` entries linked from bucket `TAILQ`s and supports lookup, optional insert-on-miss for fixed-size values, and bucket lock handoff to callers.

## Important APIs, Types, and Functions
`__wt_hash_map_init` allocates the `WT_HASH_MAP`, bucket array, and per-bucket spin locks. `__wt_hash_map_destroy` frees every item, its copied key and data, destroys locks, and nulls the caller's map pointer. `__wt_hash_map_get` performs lookup and can insert a zeroed fixed-size value when `insert_if_not_found` is true. `__wt_hash_map_unlock` releases the bucket lock retained by a successful `get(..., keep_locked=true)`. The static `__hash_map_insert_new` allocates and inserts a new item into an already locked bucket.

## Control Flow
Initialization allocates arrays sized by `hash_size`, initializes every bucket queue, then initializes every bucket lock. Lookup hashes the key with `__wt_hash_city64(key, key_size) % hash_size`, locks that bucket, scans entries with size and `memcmp` equality, and either returns the stored data pointer or inserts a fixed-size zeroed item. Error paths release locks unless the caller explicitly requested a successful locked return.

## State and Persistence Behavior
Map state is entirely in memory: bucket queues, bucket locks, copied keys, copied values, `hash_size`, and an externally configured `value_size`. There is no resizing, disk persistence, or background cleanup. Data pointers returned by `get` are owned by the map and remain valid until removal by destroy.

## Dependencies and Integration Points
The map depends on WiredTiger allocation helpers, spin locks, `TAILQ`, and `__wt_hash_city64`. It is intended for internal components that need a simple synchronized key/value table without adopting a larger indexing structure. The `keep_locked` option allows callers to perform compound operations on the returned value while holding the bucket lock.

## Risks
`hash_size` must be nonzero or bucket selection divides by zero. Insert-on-miss requires `hash_map->value_size` to be set; otherwise the function returns `EINVAL`. There is no delete API or growth policy, so long-lived maps with many keys can develop long bucket chains. The `keep_locked` contract is sharp: callers must call `__wt_hash_map_unlock` with the same key bytes and size, and must not use it after a failed get.

## Test Signals
Tests should cover init failure cleanup, destroy of null and populated maps, collision chains, get-not-found returning `WT_NOTFOUND`, fixed-size insert-on-miss zeroing, data size reporting, keep-locked mutation followed by explicit unlock, and concurrent access to separate and identical buckets. Edge tests should reject insert-on-miss when `value_size` is zero.
