# sources/storage-engines/rocksdb/utilities/persistent_cache/block_cache_tier_metadata.h

Purpose: declares `BlockInfo` and `BlockCacheTierMetadata`, the two-index metadata structure for disk-backed persistent cache.

Important APIs/types: `BlockInfo` stores a string key and `LBA`. `BlockCacheTierMetadata` exposes file insertion/lookup, block insertion/lookup/removal, LRU file eviction, and full clear. It defines hash/equality functors for cache ids and block keys.

Control flow and state: the cache-file index is an `EvictableHashTable` keyed by `BlockCacheFile::cacheid()`, giving lookup pinning and LRU eviction. The block index is a striped `HashTable` mapping `BlockInfo*` keys to the stored `BlockInfo*`. Reverse links from `BlockCacheFile::block_infos()` allow file eviction to remove all keys belonging to that file.

Dependencies and integration: includes `block_cache_tier_file.h`, `hash_table.h`, `hash_table_evictable.h`, and `lrulist.h`. It is private infrastructure for `BlockCacheTier`.

Risks and test signals: default capacities are fixed at 1M blocks and 10K files; workloads beyond that increase chain length because the hash table does not resize. Memory ownership is manual: inserts allocate `BlockInfo`, clear/evict/delete paths must free it exactly once.
