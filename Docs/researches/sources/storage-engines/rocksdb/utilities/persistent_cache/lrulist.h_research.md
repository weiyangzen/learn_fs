# sources/storage-engines/rocksdb/utilities/persistent_cache/lrulist.h

Purpose: implements an intrusive LRU list with reference-aware eviction for persistent-cache data structures.

Important APIs/types: `LRUElement<T>` provides `next_`, `prev_`, and atomic `refs_`. `LRUList<T>` exposes `Push`, `Unlink`, `Pop`, `Touch`, and `IsEmpty`. The list treats `head_` as cold and `tail_` as hot.

Control flow and state: `Push()` inserts at the cold head. `Touch()` unlinks an element and appends it at the hot tail. `Pop()` scans from `head_` until it finds an element with `refs_ == 0`, unlinks it, and returns it; referenced entries are skipped. All list mutations take a `port::Mutex`.

Dependencies and integration: used by `EvictableHashTable`, with element storage embedded in `BlockCacheFile` and `VolatileCacheTier::CacheData`.

Risks and test signals: intrusive pointers require each object to be present in at most one list and correctly unlinked before destruction. The list lock nests inside hash-table stripe locks in evictable table operations, so lock ordering must remain stable. Tests indirectly cover push/touch/evict through `hash_table_test.cc`.
