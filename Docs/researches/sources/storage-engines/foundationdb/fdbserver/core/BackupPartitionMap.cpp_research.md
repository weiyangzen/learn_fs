# sources/storage-engines/foundationdb/fdbserver/core/BackupPartitionMap.cpp

## Purpose
Builds backup partition key ranges from shard metrics and serializes partition metadata to JSON. The goal is to split user keyspace into roughly byte-balanced ranges for partitioned backup work.

## Important APIs, Types, and Functions
- `serializePartitionListJSON()` converts a `PartitionMap` into a JSON object with partition id and printable key bounds.
- `calculateBackupPartitionKeyRanges(KeyRangeMap<ShardTrackedData>* shards)` waits for shard metrics, sums user shard bytes, and emits contiguous partition ranges.

## Control Flow
The calculation loops until every normal-key shard has populated metrics in its `AsyncVar`. It then computes `targetBytesPerPartition` from `BACKUP_NUM_OF_PARTITIONS`, walks shards in key order, accumulates bytes, and cuts a partition whenever the target is reached or the last shard is reached.

## State and Persistence Behavior
No durable state is written. The function reads live shard metric caches and returns an in-memory vector of `KeyRange`s. JSON serialization is pure and depends only on the supplied partition map.

## Dependencies and Integration Points
Uses `KeyRangeMap`, `ShardTrackedData`, `ShardMetrics`, `StorageMetrics`, `normalKeys`, JSON builder utilities, and client knobs. It is intended for backup agents or management paths that need partitioned backup work assignment.

## Risks and Edge Cases
If metrics are delayed, the actor waits on the first missing shard metrics notification and restarts collection. Zero-byte totals can produce a target of zero, causing partition cuts at every shard or the single normal range depending on map shape. The algorithm does not split inside a shard, so highly skewed shard sizes can produce imbalanced partitions.

## Test Signals
Embedded tests cover no user shards, a single shard, varying sizes, zero-size shards, asynchronous metrics population, and many small shards. These validate contiguity and expected partition counts.
