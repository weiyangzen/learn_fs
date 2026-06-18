# sources/storage-engines/rocksdb/db/compaction/compaction.h

## Purpose

This header declares the core `Compaction` metadata class and related helper structures for RocksDB compaction. It defines how selected input files, output placement, compression, snapshots, deletion optimizations, table properties, blob GC, temperature, subcompaction eligibility, and per-key placement metadata are represented for a compaction job.

## Important APIs and Types

- `sstableKeyCompare(...)`: overload set for comparing SST boundary keys using user keys and range tombstone sentinel awareness.
- `AtomicCompactionUnitBoundary`: stores smallest/largest internal-key pointers spanning one or more neighboring SSTs that must be treated atomically for range tombstone truncation.
- `CompactionInputFiles`: groups input files by physical level and stores per-file atomic boundaries. Provides `empty`, `size`, `clear`, and index access.
- `Compaction`: non-copyable class encapsulating all compaction metadata.
- `Compaction::ProximalOutputRangeType`: classifies whether per-key placement to the proximal level is unsupported, full-range, non-last-level range, or disabled.
- `PerKeyPlacementContext`: debug-only helper carrying key/value/seqno and an output flag for per-key placement tests.
- `TotalFileSize(files)`: helper declaration for summing input sizes.

## Key `Compaction` Surface

Selection and file access:

- `level`, `start_level`, `output_level`, `num_input_levels`, `num_input_files`, `input`, `inputs`, `input_levels`, `filtered_input_levels`, and `boundaries`.
- `input_version`, `column_family_data`, and `edit`.

Output configuration:

- `max_output_file_size`, `target_output_file_size`, `output_compression`, `output_compression_opts`, `output_path_id`, `output_temperature_override` through `GetOutputTemperature`, `max_compaction_bytes`, and `max_subcompactions`.
- `GetOutputSplitKey` supports round-robin compaction output splitting.
- `OutputFilePreallocationSize()` estimates file preallocation.

Optimization and lifecycle:

- `IsTrivialMove`, `deletion_compaction`, `AddInputDeletions`, `ReleaseCompactionFiles`, `ResetNextCompactionIndex`, `MarkFilesBeingCompacted`, `CalculateTotalInputSize`, `InputLevelSummary`, and `Summary`.
- `KeyNotExistsBeyondOutputLevel` and `KeyRangeNotExistsBeyondOutputLevel` support deletion/range tombstone dropping.
- `IsOutputLevelEmpty`, `ShouldFormSubcompactions`, and `DoesInputReferenceBlobFiles`.

Filtering, factories, and properties:

- `CreateCompactionFilter`, `CreateSstPartitioner`, `GetOrInitInputTableProperties`, `GetInputTableProperties`, `SetOutputTableProperties`, and `GetOutputTableProperties`.

Compaction classification and telemetry:

- `score`, `bottommost_level`, `is_last_level`, `is_full_compaction`, `is_manual_compaction`, `trim_ts`, `compaction_reason`, `grandparents`, `MaxInputFileNewestKeyTime`, `MinInputFileOldestAncesterTime`, and `MinInputFileEpochNumber`.
- Listener state guards: `SetNotifyOnCompactionCompleted`, `ShouldNotifyOnCompactionCompleted`, `SetNotifyOnCompactionPreCommitCalled`, and `WasNotifyOnCompactionPreCommitCalled`.

Blob GC and per-key placement:

- `enable_blob_garbage_collection`, `blob_garbage_collection_age_cutoff`, `SupportsPerKeyPlacement`, `GetProximalLevel`, `OverlapProximalLevelOutputRange`, `TEST_AssertWithinProximalLevelOutputRange`, `EvaluateProximalLevel`, `GetKeepInLastLevelThroughSeqno`, and `OutputToNonZeroMaxOutputLevel`.

## State and Persistence Behavior

The header exposes in-memory state that drives persistent LSM changes. `Compaction` owns input metadata vectors and cached table-property maps, refs a `Version`/`ColumnFamilyData` after finalization, and owns a `VersionEdit` used to remove input files from the manifest. It stores output level/path/compression/temperature and blob GC decisions that determine newly written SST metadata. It also tracks transient flags for listener notification and file `being_compacted` lifecycle.

## Dependencies and Integration Points

The class is tightly integrated with `db/version_set.h`, `db/snapshot_checker.h`, `options/cf_options.h`, `memory/arena.h`, `rocksdb/sst_partitioner.h`, `ColumnFamilyData`, `VersionStorageInfo`, `CompactionFilter`, `TablePropertiesCollection`, internal key format, and RocksDB option structures. It is a central bridge between compaction picker decisions and compaction job execution.

## Risks and Edge Cases

- The constructor takes many parameters; callers must keep level ordering, output level, path id, compression, snapshot checker, and reason consistent.
- The header makes clear that `GetOrInitInputTableProperties()` may open/read table files and must not be called under the DB mutex.
- `filtered_input_levels()` is meaningful only when non-start-level files are filtered due to standalone range tombstones.
- Per-key placement is still guarded by internal checks and debug-only helpers, with output range semantics split across enum state, key boundaries, and keep-in-last-level sequence numbers.
- `MarkFilesBeingCompacted()` asserts the target state differs, so double marking or double release is a correctness bug.

## Test Signals

Tests reach this API through DB compaction jobs, compact-files tests, column-family compaction scheduling tests, UDT/range-deletion tests, and debug sync points. Header-specific helper behavior is also exercised by internal unit tests that call `TEST_IsBottommostLevel`, proximal placement hooks, trivial-move decisions, and table-property/filter/partitioner paths.
