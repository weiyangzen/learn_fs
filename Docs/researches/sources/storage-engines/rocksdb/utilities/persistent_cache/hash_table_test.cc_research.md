# sources/storage-engines/rocksdb/utilities/persistent_cache/hash_table_test.cc

Purpose: unit tests for the custom `HashTable` and `EvictableHashTable` implementations used by persistent-cache metadata.

Important APIs/tests: `HashTableTest` defines value-type `Node` and tests inserting 1M key/value pairs plus lookup verification, then random erasure of 1024 keys and full verification. `EvictableHashTableTest` defines pointer-type `Node` inheriting `LRUElement` and checks that 1M inserted nodes can all be evicted with intact values.

Control flow and state: tests explicitly clear maps in fixture destructors, satisfying the hash table destructor's empty-bucket assertions. Lookup tests use the returned read lock and unlock it after checking the copied node.

Dependencies and integration: uses RocksDB test harness, DB test utilities, random utilities, and the persistent-cache hash/LRU templates.

Risks and test signals: coverage is single-threaded despite the implementation targeting multi-core contention. Eviction ordering is intentionally not checked. The tests are expensive enough to allocate many large strings, so they are functional correctness signals rather than lightweight regression tests.
