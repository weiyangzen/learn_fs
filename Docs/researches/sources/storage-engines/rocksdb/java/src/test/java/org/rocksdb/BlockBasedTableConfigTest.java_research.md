# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/BlockBasedTableConfigTest.java

## Purpose
`BlockBasedTableConfigTest` validates Java bindings for block-based table configuration and several integration effects involving OPTIONS files, caches, persistent cache, and invalid format versions.

## Important APIs and Types
It covers `BlockBasedTableConfig`, `IndexType`, `DataBlockIndexType`, `ChecksumType`, `IndexSearchType`, `IndexShorteningMode`, `Cache`, `LRUCache`, `Statistics`, `TickerType`, `PersistentCache`, `Logger`, `DBOptions`, `Options`, `BloomFilter`, and `RocksDB`.

## Control Flow, State, and Persistence
Simple tests set one option and assert the getter. `jniPortal` opens DBs with selected table config values, reads generated `OPTIONS` files via `Files.walk`, and asserts native option serialization contains expected strings. Cache integration opens multiple shard DBs sharing an LRU cache and statistics, flushes/reads a key, and expects block cache add ticker increments. Invalid format version tests assert negative versions fail Java assertion and huge versions fail DB open. Deprecated tests document no-op or legacy behavior.

## Dependencies and Integration Points
Depends on JUnit, AssertJ, temp folders, Java NIO filesystem APIs, RocksDB native library, and table/cache/statistics bindings.

## Risks and Test Signals
This is strong coverage for JNI option translation and persistence into OPTIONS files. It is sensitive to options-file formatting, ticker semantics, and native defaults. An ignored import exists but no active ignored test. Filesystem cleanup calls `RocksDB.destroyDB` after reading options.
