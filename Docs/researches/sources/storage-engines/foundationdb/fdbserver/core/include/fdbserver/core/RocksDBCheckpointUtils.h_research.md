# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/RocksDBCheckpointUtils.h

## Purpose
This header declares RocksDB-specific checkpoint metadata, SST reader/writer abstractions, and checkpoint fetch/read/delete helpers used by data movement and storage recovery paths.

## Important APIs, Types, And Functions
Interfaces include `ICheckpointByteSampleReader`, `IRocksDBSstFileWriter`, and `IRocksDBSstFileReader`. Metadata types include `CheckpointFile`, `SstFileMetaData`, `LiveFileMetaData`, `RocksDBColumnFamilyCheckpoint`, `RocksDBCheckpoint`, and `RocksDBCheckpointKeyValues`. Functions include `fetchRocksDBCheckpoint`, `getTotalFetchedBytes`, `deleteRocksCheckpoint`, `newRocksDBCheckpointReader`, `newCheckpointByteSampleReader`, `newRocksDBSstFileWriter`, `newRocksDBSstFileReader`, and typed accessors `getRocksCF`, `getRocksCheckpoint`, and `getRocksKeyValuesCheckpoint`.

## Control Flow
Checkpoint fetchers copy RocksDB checkpoint files to a local directory and may call a progress callback so retries can resume. Readers expose either chunks, key-values, byte samples, or range-restricted SST reads.

## State And Persistence Behavior
The metadata serializes file paths, logical ranges, sizes, RocksDB live-file fields, checksums, sequence numbers, levels, fetched flags, and target ranges. It represents on-disk checkpoint files and fetch progress.

## Dependencies And Integration Points
It depends on Native API, `ServerCheckpoint`, Flow futures, RocksDB metadata conventions, and `CheckpointMetaData`. It integrates with `IKeyValueStore::checkpoint`, physical shard/data movement, checkpoint transfer, and RocksDB SST ingestion.

## Risks And Edge Cases
Path handling, checksum/metadata drift from RocksDB upstream, resumable fetch consistency, range tombstone bounds, and logical-vs-file byte accounting are risky. Deprecated fields remain for compatibility.

## Test Signals
Tests should validate metadata serialization, fetch resume after interruption, logical byte totals, range-restricted reads, SST writer/reader round trips, checksum validation, and cleanup of fetched checkpoint files.
