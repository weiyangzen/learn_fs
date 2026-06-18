# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/BackupPartitionMap.h

## sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/BackupPartitionMap.h

Purpose: declares backup partition data structures and helpers for dividing user keyspace into backup ranges.

Important APIs/types: `Partition`, `PartitionList`, `PartitionMap`, `serializePartitionListJSON`, and `calculateBackupPartitionKeyRanges`.

Control flow and state: `Partition` stores an integer partition ID and a `KeyRange` with serialization support. `PartitionMap` maps `Tag` to ordered `PartitionList`; a note requires ordered `std::map` behavior so multiple backup workers uploading the same content to blob storage avoid conflicts caused by nondeterministic ordering. `calculateBackupPartitionKeyRanges` uses shard tracked data to produce balanced contiguous key ranges.

Dependencies and integration: depends on FDB types, `KeyRangeMap`, and `ShardMetrics`. It integrates with backup workers and blob storage metadata production.

Risks and tests: deterministic ordering is a correctness requirement for concurrent uploads. Partitioning quality depends on shard byte-size estimates. Tests should cover JSON stability, tag ordering, empty/small/large shard maps, contiguous range coverage, and no overlap/gap invariants.
