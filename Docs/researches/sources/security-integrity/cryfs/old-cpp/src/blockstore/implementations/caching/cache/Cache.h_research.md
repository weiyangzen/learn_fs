# sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/caching/cache/Cache.h

Purpose: Implements a bounded, time-purged, addressable cache template used by the legacy caching blockstore layer. Values are evicted by age or capacity, and value destruction can occur in parallel outside the main cache mutex.

Important APIs and types: `Cache<Key, Value, MAX_ENTRIES>` exposes `size`, `push`, `pop`, and `flush`. Constants are `PURGE_LIFETIME_SEC`, `PURGE_INTERVAL`, and `MAX_LIFETIME_SEC`. Internal types include `QueueMap<Key, CacheEntry<Key, Value>>`, `cpputils::LockPool<Key>`, `MutexPoolLock`, and `PeriodicTask`.

Control flow: Construction starts a periodic task that calls `_deleteOldEntriesParallel`. `push` locks, ensures capacity with `_makeSpaceForEntry`, then appends a `CacheEntry`. `pop(key)` locks the cache and a per-key flush lock, removes the entry if present, and releases the wrapped value. `_deleteEntry` peeks the oldest key, locks that key against concurrent pop, removes it, unlocks the cache while the value destructor runs, then re-locks. Flush and age-based deletion fan out `2 * hardware_concurrency` async workers that repeatedly delete matching entries at the queue front.

State and persistence behavior: State is in-memory queue/map entries plus a background purge thread. Persistence behavior is indirect: `Value` destructors may flush dirty blocks or release resources, so eviction timing affects when underlying storage writes happen.

Dependencies and integration points: Depends on `CacheEntry`, `QueueMap`, `PeriodicTask`, Boost optional, futures/async, cpp-utils assertions and lock pools. Used by caching blockstore code to hold recently accessed blocks and flush old entries.

Risks: Eviction is front-only, so only old entries at the beginning are purged; newer front entries can block older-but-later entries if ordering assumptions change. Destructors run outside the mutex for parallelism, which is powerful but concurrency-sensitive. The destructor does not explicitly stop `_timeoutFlusher` before deleting entries, relying on member destruction order after the destructor body; callbacks into a partly destructing object are a risk if `PeriodicTask` does not stop promptly. Duplicate `push` keys throw through `QueueMap`.

Test signals: There are TODOs for flush testing. Effective coverage should assert size bounds, duplicate handling, pop behavior, destructor/flush side effects, age purge, capacity eviction, and concurrent pop/evict safety.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/caching/cache/Cache.h` completely for this pass (181 lines, 7973 bytes).
