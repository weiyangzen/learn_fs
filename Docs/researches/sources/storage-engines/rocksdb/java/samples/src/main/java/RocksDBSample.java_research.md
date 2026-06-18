# sources/storage-engines/rocksdb/java/samples/src/main/java/RocksDBSample.java

## Purpose
This broad sample demonstrates core RocksJava APIs: options configuration, table and memtable factories, cache/filter/rate limiter setup, basic put/get/delete, write batches, statistics, iterators, and multi-get.

## Important APIs, Types, and Functions
It uses `Options`, `Filter`, `BloomFilter`, `ReadOptions`, `Statistics`, `RateLimiter`, `RocksDB`, compression and compaction enums, memtable configs, `PlainTableConfig`, `BlockBasedTableConfig`, `Cache`, `LRUCache`, `WriteOptions`, `WriteBatch`, ticker and histogram enums, `RocksIterator`, and `multiGetAsList`.

## Control Flow
The program validates a DB path argument, tries opening a missing DB and expects an exception, configures options and asserts round-trip option values, switches memtable and table factories, opens a DB for basic property checks, then reopens for a larger scenario. It writes multiplication-table keys, uses write batches for more keys, tests byte-array `get` overloads with insufficient and sufficient buffers, deletes data, writes with explicit `WriteOptions`, reads statistics, iterates forward and backward, seeks, collects keys, and multi-gets values with and without read options.

## State and Persistence Behavior
The sample creates persistent DB state at the provided path and many test keys. It mutates option objects, cache/filter/rate-limiter configuration, DB data, and iterator state. Resources are mostly scoped with try-with-resources.

## Dependencies and Integration Points
It exercises many public Java APIs and their JNI bridges, including ordinary DB operations, write batch bridges, iterator bridges, option bridges, statistics, and multi-get conversion.

## Risks and Edge Cases
Assertions require `-ea`. Existing DB contents may affect iteration and multi-get assumptions. Some resources such as `Cache cache` are not in try-with-resources in this sample. The sample catches final `RocksDBException` by printing rather than failing.

## Test Signals
This file is a compact integration smoke test for option setters/getters, open failure handling, byte-array get length contracts, not-found constants, write batch persistence, statistics enum coverage, iterator validity/status, seek behavior, and multi-get result size matching.
