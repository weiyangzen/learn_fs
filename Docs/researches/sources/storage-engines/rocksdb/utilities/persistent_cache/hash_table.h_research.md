# sources/storage-engines/rocksdb/utilities/persistent_cache/hash_table.h

Purpose: implements a fixed-size, striped-lock hash table optimized for concurrent persistent-cache metadata lookups.

Important APIs/types: template `HashTable<T, Hash, Equal>` provides `Insert`, `Find`, `Erase`, `GetMutex`, and `Clear`. `Find` has a special contract: it returns with the bucket read lock still held via `ret_lock`, so callers can safely inspect returned data until they unlock.

Control flow and state: construction computes bucket count from capacity/load factor, allocates bucket and lock arrays, and `mlock`s them on Linux. Operations hash the key to a bucket and then to one of `nlocks_` locks. Buckets use `std::list<T>` collision chains and no resizing. Destruction asserts all buckets have been cleared.

Dependencies and integration: used by `BlockCacheTierMetadata`, `EvictableHashTable`, volatile cache, tests, and the hash-table benchmark. It depends on RocksDB mutex wrappers and Linux `mlock` when available.

Risks and test signals: lack of resizing means bad capacity estimates degrade lookup/insert/erase latency. The lock handoff API is easy to misuse; failing to unlock after `Find` deadlocks a stripe. Unit tests cover million-key insert/lookup and erase behavior, but not concurrent correctness under thread sanitizer.
