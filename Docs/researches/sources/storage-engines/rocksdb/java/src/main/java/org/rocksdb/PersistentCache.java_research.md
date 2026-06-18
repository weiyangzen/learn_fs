# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/PersistentCache.java research

## Purpose

`PersistentCache` wraps RocksDB's persistent read cache, intended for caching I/O pages on persistent media such as SSD or NVM.

## Important APIs and types

The constructor accepts `Env`, cache path, size, `Logger`, and `optimizedForNvm`, then calls native `newPersistentCache(...)`. Disposal calls `disposeInternalJni(handle)`.

## Control flow

Construction creates the native persistent cache or throws `RocksDBException`. Java code then passes the cache to table or DB configuration paths that support persistent cache use. There are no Java getters or mutators in this wrapper.

## State and persistence behavior

The object owns a native cache handle. Unlike `LRUCache`, cache data can live on persistent storage under the configured path, but it remains a cache: DB correctness must not depend on cached contents.

## Dependencies and integration points

It depends on `Env`, `Logger`, `RocksObject`, and native persistent-cache creation. It integrates with table reader/block cache configuration outside this file.

## Risks and test signals

Risks include path permissions, size validation, logger lifetime, native memory/resource cleanup, and cache contents surviving process restarts in ways tests must account for. Tests should create a cache in a temp directory, attach it to read options/table config where supported, verify reads populate/hit it, and close it cleanly.
