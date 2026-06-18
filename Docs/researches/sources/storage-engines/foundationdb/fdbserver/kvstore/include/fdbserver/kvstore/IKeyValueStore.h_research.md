# sources/storage-engines/foundationdb/fdbserver/kvstore/include/fdbserver/kvstore/IKeyValueStore.h

## Purpose
This header defines the common FoundationDB key-value storage engine interface and factory declarations for SQLite, Redwood, RocksDB, sharded RocksDB, memory, and log-system-backed stores.

## Important APIs, Types, And Functions
`CheckpointRequest` describes checkpoint version, key ranges, format, ID, and target directory. `IKeyValueStore` extends `IClosable` and requires `getType`, `set`, `clear`, `commit`, `readValue`, `readValuePrefix`, `readRange`, and `getStorageBytes`. Optional extension points include `shardAware`, `supportsSstIngestion`, `canCommit`, range/shard APIs, `replaceRange`, `markRangeAsActive`, `persistRangeMapping`, `getExistingRanges`, debug `getSize`, RocksDB stats, `resyncLog`, snapshot control, checkpoint/restore/delete, compaction, `init`, and `ingestSSTFiles`.

## Control Flow
Users stage mutations with `set` and `clear`, then await `commit` for atomic durability. Reads return Flow futures and obey the documented causal consistency contract. The default `replaceRange` clears a range and writes each `KeyValueRef`, yielding every 1000 records to avoid starving the actor scheduler.

## State And Persistence Behavior
Implementations own actual persistence. The interface defines durability at `commit` and idempotent `init`, important for rollback. Checkpoints and SST ingestion expose external persisted artifacts. Shard-aware implementations maintain physical shard mappings.

## Dependencies And Integration Points
It depends on FoundationDB key/value types, checkpoints, closable lifecycle, key range maps, Flow futures, and bulk-load file maps. `openKVStore` dispatches by `KeyValueStoreType` and configuration.

## Risks And Test Signals
Default methods throw `not_implemented()` for many optional features, so callers must gate on capabilities. Causal consistency and idempotent initialization are central correctness constraints. Tests should cover mutation atomicity, read/commit interleavings, range limits, replacement yielding, checkpoint/restore compatibility, shard mapping persistence, SST ingestion errors, and factory dispatch for every store type.
