# sources/storage-engines/rocksdb/utilities/persistent_cache/volatile_tier_impl.cc

Purpose: implements `VolatileCacheTier`, an in-memory LRU persistent-cache tier that can spill evicted entries to the next tier.

Important APIs and control flow: `Insert()` pre-adds value size to `size_`, evicts until within `max_size_`, inserts a `CacheData` into the evictable hash index, and rolls size back on duplicate/eviction failure. `Lookup()` finds the key, copies the value to caller-owned memory, decrements the reference count, and returns hit; on miss it delegates to `next_tier()` if present. `Evict()` removes an LRU entry, optionally inserts it into the next tier, decrements `size_`, and deletes it. `Stats()` returns hit/miss/insert/evict counters and percentages.

State and persistence: state is entirely memory resident: `index_`, `size_`, `max_size_`, and stats. Persistence only occurs if a lower tier accepts evicted data. Destruction clears the index and deletes all `CacheData`.

Dependencies and integration: uses `EvictableHashTable`, `LRUElement`, and `PersistentCacheTier` next-tier chaining. It is used in tiered RAM+block cache tests and benchmark setup.

Risks and test signals: `Erase()` is unsupported and asserts. Duplicate inserts return `TryAgain` rather than success. `Evict()` ignores next-tier insert errors, which is acceptable for a cache but can lose data from upper-tier perspective. Most volatile/tiered stress tests are disabled.
