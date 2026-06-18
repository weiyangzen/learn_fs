# sources/storage-engines/foundationdb/fdbserver/core/RocksDBCheckpointUtils.cpp

## Purpose
`RocksDBCheckpointUtils.cpp` implements RocksDB-backed checkpoint fetching, deletion, reading, and SST file utilities for data movement and bulk-load flows. When `WITH_ROCKSDB` is not enabled, it provides safe no-op or null fallbacks for the same public factory functions.

## Important APIs, types, and functions
- Serialization helpers `getRocksCF`, `getRocksCheckpoint`, and `getRocksKeyValuesCheckpoint` deserialize checkpoint payloads.
- `fetchRocksDBCheckpoint` fetches full RocksDB column-family checkpoints or key-value range checkpoints from storage servers and updates `CheckpointMetaData`.
- `deleteRocksCheckpoint` removes local checkpoint directories/files based on checkpoint format.
- `getTotalFetchedBytes` summarizes fetched file sizes across checkpoint formats.
- `newRocksDBCheckpointReader`, `newRocksDBSstFileWriter`, `newRocksDBSstFileReader`, and `newCheckpointByteSampleReader` are public factories.
- Internal reader classes are `RocksDBColumnFamilyReader`, `RocksDBCFCheckpointReader`, `RocksDBSstFileReader`, `RocksDBSstFileWriter`, and `RocksDBCheckpointByteSampleReader`.

## Control flow
For DataMove Rocks column-family checkpoints, `fetchRocksDBCheckpoint` launches `fetchCheckpointFile` for each SST file and optionally fetches the byte-sample SST. Each file is streamed from a source storage server via `fetchCheckpoint`, written with atomic async file flags, synced, and recorded as fetched in the serialized checkpoint. For RocksDB key-value checkpoints, `fetchCheckpointRanges` compares requested ranges against already fetched files, then `fetchCheckpointRange` streams `FetchCheckpointKeyValues` replies into a local SST writer and records either a real SST path or `emptySstFilePath`.

`RocksDBColumnFamilyReader` imports exported SST metadata into a local RocksDB database under a `/reader` subdirectory, opens the checkpoint column family read-only, and serves bounded range batches through thread-pool actions. `RocksDBCFCheckpointReader` instead exposes raw file chunks for a named SST or byte-sample file. SST reader/writer wrappers provide synchronous point iteration and range reads for bulk-load helpers.

## State and persistence behavior
The code writes local SST files and temporary/readable RocksDB databases under supplied checkpoint directories. It mutates `CheckpointMetaData` by replacing remote file paths with local paths, setting `fetched` flags, and serializing updated checkpoint structures. `readerInitialized` is written to the default RocksDB column family after successful import so future opens can detect whether a `/reader` database is complete. `deleteRocksCheckpoint` recursively removes directories or files referenced by fetched checkpoint metadata.

## Dependencies and integration points
The implementation depends on RocksDB APIs (`DB`, `SstFileReader`, `SstFileWriter`, column-family import metadata), `StorageCheckpoint` data types, storage-server RPCs (`fetchCheckpoint`, `fetchCheckpointKeyValues`), Flow async files, thread pools, `MutationTracking` debug hooks, and `FDBRocksDBVersion` compile-time version checks. It is used by physical shard movement, checkpoint restore/fetch paths, and bulk-load SST range reads.

## Risks and edge cases
RocksDB version mismatch is a compile-time failure. File fetching assumes `metaData->src.front()` identifies an available source storage server; missing server-list entries raise `checkpoint_not_found`. Several functions retry only a bounded number of times. Imported reader DBs are destroyed and rebuilt if the initialization marker is absent. `RocksDBSstFileWriter::finish` intentionally returns false for empty files because RocksDB cannot finish an empty SST. `fetchCheckpointRange` has simulation failure injection and needs careful handling of partial writer output. Recursive deletion trusts metadata-derived paths, so malformed metadata would be dangerous.

## Test signals
There are no local `TEST_CASE`s. Runtime traces include `FetchCheckpointFile*`, `FetchCheckpointRange*`, `RocksDBCheckpointReader*`, `CheckpointReaderImportCheckpoint*`, `RocksDBSstFile*Error`, and `DeleteRocks*Checkpoint`. `DEBUG_MUTATION("FetchCheckpointData", ...)` can expose streamed key-values when mutation tracking is enabled.
