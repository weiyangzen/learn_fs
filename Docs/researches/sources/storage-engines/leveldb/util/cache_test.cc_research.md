# sources/storage-engines/leveldb/util/cache_test.cc

## Purpose
`cache_test.cc` validates LRU cache semantics and handle lifetime behavior.

## Important APIs, Types, and Functions
`CacheTest` wraps a `Cache`, numeric key/value encoders, insertion helpers, lookup helpers, erase helper, and a static deleter that records deleted key/value pairs.

## Control Flow
Tests insert, replace, lookup, erase, keep handles pinned across replacement/erase, overfill capacity, vary charge weights, request new ids, prune unpinned entries, and exercise zero-capacity behavior.

## State, Dependencies, and Integration
The tests depend on `leveldb/cache.h`, `util/coding`, and gtest. Deleted vectors provide precise evidence of when values are actually destroyed.

## Risks and Test Signals
The strongest signals are that pinned entries survive eviction until release and that zero capacity returns handles that are not cache-resident. No multithreaded stress is included.
