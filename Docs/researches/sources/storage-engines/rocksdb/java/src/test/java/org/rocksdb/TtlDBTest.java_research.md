# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/TtlDBTest.java

## Purpose

This suite validates Java `TtlDB` open paths, TTL expiry through compaction, iterator behavior, TTL column-family APIs, and write-batch/flush behavior.

## Important APIs and types

The file uses `TtlDB`, `Options`, `DBOptions`, `ColumnFamilyDescriptor`, `ColumnFamilyHandle`, `WriteBatch`, `WriteOptions`, `FlushOptions`, `RocksIterator`, and `TimeUnit`.

## Control flow

Tests open TTL DBs with default TTL or explicit one-second TTL, write keys, optionally sleep for two seconds, compact, and assert whether keys remain. Column-family tests configure TTL values per CF and create TTL CFs dynamically. Batch tests write multiple records through `WriteBatch`, flush default and CF handles, then read back values.

## State and persistence behavior

TTL behavior depends on persisted timestamps encoded in values and compaction to purge expired entries. A TTL of zero preserves default-CF keys, while a one-second TTL removes keys after sleep plus compaction.

## Dependencies and integration points

This suite links Java TTL wrappers to standard RocksDB write, read, iterator, column-family, compaction, and batch flush APIs.

## Risks and test signals

Risks include timing flakiness, TTL value ordering mistakes for CF lists, missing compaction purge, and incorrect default-CF identification. Signals are exact value reads before expiry, null after expiry, iterator key/value checks, and batch readback.
