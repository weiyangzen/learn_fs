# sources/storage-engines/foundationdb/fdbserver/workloads/KVStoreTest.cpp

## Purpose
Standalone storage-engine workload for exercising `IKeyValueStore` implementations outside normal transaction layers. It measures read/commit latency and checks basic read-committed/causal consistency against an in-memory version history.

## Important APIs, types, and functions
`TestHistogram` samples latency distributions. `KVTest` wraps an `IKeyValueStore`, version counters, and `allSets` history. Actors `testKVRead`, `testKVReadSaturation`, and `testKVCommit` validate and measure operations. `KVStoreTestWorkload` selects store type and options, while `testKVStoreMain` and `testKVStore` drive setup, load, random operations, optional counting, clearing, and store lifecycle.

## Control flow
Client 0 creates a key-value store by type (`SQLite`, Redwood, RocksDB, sharded RocksDB, memory, radix tree), initializes it, optionally counts existing rows, bulk-loads keys, then runs either saturation or scheduled operations. Scheduled operations choose commit, set, or read according to configured fractions. Commits are issued through an `ActorCollectionNoErrors`; reads verify returned versions relative to durable and committed version trackers. Optional clear deletes chunks at the end.

## State and persistence behavior
Database state is in the selected local KV store file or in-memory store, not FoundationDB. Values encode a `Version` plus padding. `KVTest::allSets` tracks expected version history, and close either disposes unnamed stores or closes named stores for preservation.

## Dependencies and integration points
Depends on `IKeyValueStore`, storage-engine factory functions, Flow actors, binary serialization, `IndexedSet`, deterministic random keys, and trace/perf metrics.

## Risks and test signals
Risks include high memory use from `allSets`, file lifecycle differences between named and random stores, broad ASSERT on store errors, and concurrency through asynchronous commits. Signals are consistency ASSERTs in reads, store `getError`, setup/count traces, operation counters, and latency histogram metrics.
