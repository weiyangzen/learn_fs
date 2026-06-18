# sources/storage-engines/rocksdb/utilities/persistent_cache/volatile_tier_impl.h

Purpose: declares the RAM-backed `VolatileCacheTier` implementation of `PersistentCacheTier`.

Important APIs/types: public methods include `Insert`, `Lookup`, `IsCompressed`, `Erase`, `GetPrintableOptions`, and `Stats`. Private `CacheData` stores immutable key and value strings and inherits `LRUElement`. Hash/equality functors drive an `EvictableHashTable<CacheData>`.

Control flow and state: `max_size_` and `size_` are atomics used for coarse capacity accounting. `Statistics` stores atomic hit/miss/insert/evict counters and computes hit/miss percentages. Eviction is LRU through the index/list combination.

Dependencies and integration: depends on persistent-cache tier abstractions and the persistent-cache hash/LRU templates. It can be used standalone or as the front tier in `PersistentTieredCache`.

Risks and test signals: comments say the evictable hash table is not concurrent at this point, while the tier uses atomics for counters/size; concurrent behavior depends on the underlying striped locks and correct ref handling. The constructor defaults to unlimited capacity, making eviction optional unless configured.
