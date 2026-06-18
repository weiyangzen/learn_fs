# sources/storage-engines/rocksdb/db/compaction/compaction.cc

## Purpose

This file implements the `Compaction` metadata object declared in `compaction.h`. A `Compaction` captures the selected input files, output level/path/compression/temperature decisions, snapshot and range-deletion filtering context, per-key placement metadata, blob GC settings, and helper operations used by compaction jobs, pickers, and version edits.

## Important Functions and Methods

- `sstableKeyCompare(...)`: compares SST boundary internal keys by user key without timestamp, with special ordering for range tombstone sentinel footers.
- `TotalFileSize(files)`: sums file sizes until a null entry.
- `Compaction::FinalizeInputInfo(Version*)`: attaches the owning `Version`/`ColumnFamilyData`, refs both, and sets the `VersionEdit` CF id.
- `GetBoundaryKeys()` and `GetBoundaryInternalKeys()`: compute overall user/internal key ranges for inputs, with special handling for L0 overlap.
- `PopulateWithAtomicBoundaries()`: computes atomic compaction unit boundaries for non-L0 neighboring files whose boundary user keys overlap.
- `IsBottommostLevel()` and `IsFullCompaction()`: derive bottommost/full-compaction flags from `VersionStorageInfo`.
- `InitInputTableProperties()`: lazily loads table properties for all input files.
- Constructor: initializes immutable compaction metadata, marks input files as being compacted, populates input-level briefs, computes output split key, and computes proximal output range.
- `PopulateProximalLevelOutputRange()`, `SupportsPerKeyPlacement()`, `GetProximalLevel()`, `OverlapProximalLevelOutputRange()`, `TEST_AssertWithinProximalLevelOutputRange()`, and `EvaluateProximalLevel()`: implement metadata for per-key placement when `preclude_last_level_data_seconds` allows some output to go to the proximal level.
- `IsTrivialMove()`: determines whether compaction can be represented as file movement rather than rewrite.
- `AddInputDeletions()`, `ReleaseCompactionFiles()`, `ResetNextCompactionIndex()`, `Summary()`, `InputLevelSummary()`, and `CalculateTotalInputSize()`: support version edits, picker state, logging, and accounting.
- `KeyNotExistsBeyondOutputLevel()` and `KeyRangeNotExistsBeyondOutputLevel()`: provide deletion/drop optimizations when no lower-level overlap exists.
- `OutputFilePreallocationSize()`, `CreateCompactionFilter()`, `CreateSstPartitioner()`, `IsOutputLevelEmpty()`, `ShouldFormSubcompactions()`, `DoesInputReferenceBlobFiles()`, `MaxInputFileNewestKeyTime()`, `MinInputFileOldestAncesterTime()`, `MinInputFileEpochNumber()`, and `GetOutputTemperature()`: expose compaction-job decisions and statistics inputs.
- `FilterInputsForCompactionIterator()`: excludes non-start-level input files completely shadowed by a standalone range deletion file when snapshot conditions prove it safe.

## Control Flow

Construction is the central control point:

1. Store levels, target sizes, options, grandparents, snapshot state, reason, trim timestamp, blob GC policy, and input files.
2. Call `PopulateWithAtomicBoundaries()` before storing inputs, so each non-L0 input file can carry the atomic range needed by range tombstone aggregation.
3. Compute `bottommost_level_` unless the reason is external SST ingestion or refit level.
4. Compute full-compaction/manual-compaction flags and blob GC enablement/cutoff.
5. Evaluate proximal level support. It is only possible for leveled/universal compactions outputting to the last level, with a positive `preclude_last_level_data_seconds`, and with a valid proximal level greater than L0.
6. Mark all input files `being_compacted=true`.
7. Determine max subcompactions and max output file size.
8. Build `LevelFilesBrief` arrays. If `earliest_snapshot_` is set, run `FilterInputsForCompactionIterator()` to omit files shadowed by a standalone range tombstone; otherwise include all input files.
9. Compute smallest/largest user keys and an optional output split cursor for round-robin leveled compaction.
10. Populate proximal output key range and sequence-number restrictions.

Destruction unreferences `input_version_` and `cfd_`. Actual release of `being_compacted` flags is done through `ReleaseCompactionFiles(status)`, which also informs the column family's compaction picker.

Trivial move logic rejects unsafe cases: overlapping L0 inputs, manual compactions with filters, same-level compactions, temperature-change compactions, compression/path mismatches, excessive grandparent overlap, disallowing SST partitioner decisions, and any per-key-placement compaction. Universal compaction has a separate `allow_trivial_move` path using `is_trivial_move_`.

Range-existence checks walk lower levels using monotonic `level_ptrs`, making repeated calls efficient during compaction iteration. They account for user-defined timestamps by using `CompareWithoutTimestamp()` where exact timestamp ordering would be too strict.

## State and Persistence Behavior

`Compaction` itself is in-memory metadata, but it mutates important live state:

- Input `FileMetaData::being_compacted` flags are set in the constructor and cleared in `ReleaseCompactionFiles()`.
- `edit_` records file deletions and is tagged with the column family id once `FinalizeInputInfo()` is called.
- `input_version_` and `cfd_` are reference-counted while the compaction object is active.
- Lazily loaded `input_table_properties_` and job-filled `output_table_properties_` are stored in memory and feed filters, listeners, and reports.
- Blob GC, output temperature, output path, compression, and proximal-level flags affect the physical output files written by compaction jobs, although the file does not write SSTs itself.

## Dependencies and Integration Points

This implementation depends on `ColumnFamilyData`, `Version`, `VersionStorageInfo`, `VersionEdit`, `FileMetaData`, internal key comparators, table property loading, `CompactionFilterFactory`, `SstPartitionerFactory`, `MutableCFOptions`, `ImmutableOptions`, blob-file metadata, `SnapshotChecker`, and `SyncPoint` test hooks. It is consumed by compaction pickers, `CompactionJob`, flush/compaction scheduling, listener notification code, and deletion/range-tombstone optimization paths.

## Risks and Edge Cases

- `sstableKeyCompare()` must distinguish range tombstone sentinel boundaries without treating adjacent SSTs as overlapping incorrectly.
- Failing to call `ReleaseCompactionFiles()` would leave input files marked as compacting and block future picks.
- `FilterInputsForCompactionIterator()` is intentionally limited: it requires no user-defined timestamp, a standalone range-deletion file, safe snapshot visibility, and does not support older-L0-by-newer-L0 filtering.
- Proximal-level placement has explicit FIXME notes: some ranges may disable proximal output because smallest/largest proximal keys are not populated, and `proximal_output_range_type_` is not fully used.
- Trivial move must consider filters, path id, compression, grandparent overlap, partitioner constraints, L0 overlap, temperature changes, and per-key placement.
- Lazy table property loading logs and clears all cached properties on the first read failure.

## Test Signals

Relevant test coverage appears across compaction and DB tests, including compact-files trivial-move tests, column-family manual/automatic compaction conflict tests, write-stall and speedup tests, range-deletion/UDT flush and compaction tests, and sync-point hooks such as `Compaction::InputCompressionMatchesOutput:*` and `Compaction::SupportsPerKeyPlacement:Enabled`.
