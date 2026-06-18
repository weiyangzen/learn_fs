# sources/storage-engines/leveldb/include/leveldb/cache.h

Purpose: declares the thread-safe cache interface and built-in LRU cache factory used for blocks, opened tables, and other internal caches.

Important APIs and types: `Cache`, opaque `Cache::Handle`, `NewLRUCache`, `Insert`, `Lookup`, `Release`, `Value`, `Erase`, `NewId`, `Prune`, and `TotalCharge`.

Control flow: clients insert charged values with a deleter, receive handles from insert/lookup, access values through handles, and release handles when done. Erase removes the key but active handles keep the entry alive until release.

State and persistence behavior: cache contents are memory-only. Charges approximate capacity consumption; `NewId` lets different clients partition key spaces.

Dependencies and integration: table cache uses it for table handles; block cache uses it for table blocks. Depends on `Slice` keys and exported symbol visibility.

Risks and edge cases: callers must release every handle exactly once. Deleters must understand the key/value lifetime supplied by the implementation. Default `Prune` is a no-op unless overridden.

Test signals: cache behavior is tested elsewhere; in this subset it is exercised indirectly through `TableCache`.
