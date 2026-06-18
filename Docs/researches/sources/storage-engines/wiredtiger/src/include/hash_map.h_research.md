## sources/storage-engines/wiredtiger/src/include/hash_map.h

Purpose: this header defines WiredTiger's simple generic hash map container. The comments explicitly position it for low-performance use cases and prototyping rather than highly optimized hot paths.

Important APIs/types/functions: `WT_HASH_MAP_ITEM` stores a `TAILQ_ENTRY`, owned `key` and `data` pointers, and their sizes. `WT_HASH_MAP` stores an array of bucket heads (`TAILQ_HEAD(__wt_hash_map_hash, __wt_hash_map_item) *hash`), a parallel array of `WT_SPINLOCK` bucket locks, the bucket count `hash_size`, and optional fixed `value_size`. Functions are declared in `extern.h`: `__wt_hash_map_init`, `__wt_hash_map_get`, `__wt_hash_map_destroy`, and `__wt_hash_map_unlock`.

Control flow: callers initialize a map with a chosen bucket count, then call `__wt_hash_map_get` with key bytes and options to insert if missing and optionally keep the bucket lock held. Items are stored on per-bucket tail queues. If a caller keeps the lock, it must later call `__wt_hash_map_unlock` with the same key information. Destroy releases the map, locks, and owned item memory.

State and persistence behavior: all map state is in memory. The map owns key and value allocations, so callers must treat returned data as map-owned and should not free it directly. No durable state is written.

Dependencies and integration points: it depends on queue macros (`TAILQ_ENTRY`, `TAILQ_HEAD`), `WT_SPINLOCK`, memory allocation helpers, and declarations in `extern.h`. It can be used by subsystems needing modest keyed lookup without adding a specialized data structure.

Risks: bucket count selection affects performance and collision behavior. The keep-locked option creates an obligation that is easy to violate, leading to deadlock. Because the map owns memory, storing pointers to external lifetime-managed data as values would be risky unless copied as intended. It is not optimized for high-contention hot paths.

Test signals: unit tests for insert/find/missing-key behavior, duplicate key handling, fixed and variable value sizes, collision-heavy workloads, keep-locked/unlock pairing, and destroy-time leak checks are relevant.
