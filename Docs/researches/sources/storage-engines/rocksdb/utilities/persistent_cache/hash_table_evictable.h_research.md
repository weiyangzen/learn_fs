# sources/storage-engines/rocksdb/utilities/persistent_cache/hash_table_evictable.h

Purpose: layers LRU eviction on top of the striped `HashTable` for pointer types, used by cache files and volatile cache entries.

Important APIs/types: `EvictableHashTable<T,Hash,Equal>` exposes `Insert`, `Find`, `Evict`, `Clear`, `GetMutex`, and debug LRU assertions. Each lock stripe has an `LRUList<T>`, and each object must inherit compatible `LRUElement` fields.

Control flow and state: insert adds to the hash bucket and pushes the object at the cold end of the stripe LRU. find increments `refs_` and touches the object to the hot end. eviction picks a random stripe start and scans stripes for an unreferenced LRU entry, erasing it from the bucket and optionally invoking a callback. clear unlinks every object from its stripe LRU and calls a deleter.

Dependencies and integration: depends on `HashTable`, `LRUList`, and `Random::GetTLSInstance()`. It is central to cache-file eviction in `BlockCacheTierMetadata` and RAM-key eviction in `VolatileCacheTier`.

Risks and test signals: callers must decrement `refs_` after using found objects; otherwise eviction can stall. Eviction is approximate across stripes, not global LRU. Tests validate bulk eviction returns valid values but do not assert exact ordering because stripe selection is randomized.
