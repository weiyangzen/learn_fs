# sources/storage-engines/rocksdb/utilities/persistent_cache/block_cache_tier_metadata.cc

Purpose: implements the metadata manager joining block keys to logical addresses and cache-file ids to evictable file objects.

Important APIs and control flow: `Insert(BlockCacheFile*)` adds a file to the evictable file index. `Lookup(cache_id)` returns a file and relies on `EvictableHashTable::Find()` to increment `refs_`. `Insert(key,lba)` allocates `BlockInfo` and inserts it into the block index. `Lookup(key,lba)` obtains the striped read lock from `HashTable::Find()`, copies the LBA, and releases the lock. `Evict()` asks the file index for an LRU candidate and passes `RemoveAllKeys()` as a callback. `Clear()` deletes all file and block metadata.

State and persistence: all metadata is in memory. `RemoveAllKeys()` uses the file's reverse `block_infos()` list to erase every block index entry pointing at a file before the file is deleted. There is no on-disk metadata replay.

Dependencies and integration: wraps `HashTable<BlockInfo*>` and `EvictableHashTable<BlockCacheFile>`, using `BlockCacheFile`'s LRU/reference fields. `BlockCacheTier` calls it for insert, lookup, erase, eviction, and close.

Risks and test signals: `Remove()` asserts successful erase, so absent-key erases are not tolerated. `Lookup(cache_id)` leaves reference decrementing to callers after `Read()`. The active tests exercise hash table operations independently and persistent-cache lookup through DB tests; direct metadata eviction is covered mainly by disabled persistent-cache stress tests.
