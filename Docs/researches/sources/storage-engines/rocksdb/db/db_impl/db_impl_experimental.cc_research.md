<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_impl/db_impl_experimental.cc -->
# sources/storage-engines/rocksdb/db/db_impl/db_impl_experimental.cc

## Purpose

`db_impl_experimental.cc` implements two experimental `DBImpl` maintenance APIs: `SuggestCompactRange()` and `PromoteL0()`. Both manipulate compaction metadata directly under the DB mutex to influence LSM layout without performing a normal write-path operation.

`SuggestCompactRange()` marks existing files in a key range as compaction candidates and schedules background compaction. `PromoteL0()` performs a metadata-only promotion of non-overlapping L0 files into an empty target level by writing a MANIFEST edit.

## Important APIs, Types, and Functions

- `SuggestCompactRange(ColumnFamilyHandle*, const Slice* begin, const Slice* end)` converts optional user-key bounds to internal min/max keys, scans non-last non-empty levels for overlapping files, sets `FileMetaData::marked_for_compaction`, recomputes compaction score, enqueues the CF, and schedules background work.
- `PromoteL0(ColumnFamilyHandle*, int target_level)` validates the target level, sorts L0 files by largest key, rejects files currently compacting or overlapping L0 ranges, verifies levels `1..target_level` are empty, writes a `VersionEdit` that deletes files from L0 and adds them to the target level, applies the edit through `VersionSet::LogAndApply()`, and publishes a `SuperVersion`.
- Supporting types include `ColumnFamilyHandleImpl`, `ColumnFamilyData`, `VersionStorageInfo`, `InternalKey`, `InternalKeyComparator`, `FileMetaData`, `VersionEdit`, `JobContext`, `ReadOptions`, and `WriteOptions`.

## Control Flow

`SuggestCompactRange()` is advisory. It casts the handle, builds internal bound keys only for provided endpoints, locks `mutex_`, then iterates from level 0 through the level before the highest non-empty level. For each level it calls `GetOverlappingInputs()` and flips `marked_for_compaction` on each overlapping file. After marking, it recomputes compaction scores with latest mutable CF options and `full_history_ts_low`, enqueues pending compaction for the column family, and invokes `MaybeScheduleFlushOrCompaction()`.

`PromoteL0()` is stricter because it directly changes persistent LSM metadata. It rejects `target_level < 1`, then under `mutex_` rejects target levels outside the configured number of levels. It copies and sorts L0 file metadata by largest internal key, checks no file is already being compacted, and verifies adjacent sorted files do not overlap. It then requires every level from 1 through the target to be empty. Only after these invariants pass does it build a `VersionEdit` deleting each file from L0 and adding the same file metadata to the target level. `LogAndApply()` persists the edit to MANIFEST; on success `InstallSuperVersionAndScheduleWork()` makes the new layout visible and schedules any resulting work.

## State and Persistence Behavior

`SuggestCompactRange()` changes in-memory file metadata by setting `marked_for_compaction`. It does not write a manifest edit itself, but recomputed compaction score and queueing can lead to future compactions that persist new SST/MANIFEST state.

`PromoteL0()` is a manifest-persisted metadata move. It does not rewrite SST bytes and does not create new table files. The same file numbers, sizes, key bounds, sequence bounds, temperature, blob linkage, checksums, unique IDs, range-deletion sizes, tail sizes, timestamp persistence flags, and min/max timestamps are re-added at the target level. Its successful completion installs a new `SuperVersion`, flushes the info log, and cleans the `JobContext`.

Neither function flushes memtables first. They operate on the current version's files and assume their invariants are sufficient for safe metadata manipulation.

## Dependencies and Integration Points

These APIs depend on `db_impl.h`, `column_family.h`, `version_set.h`, `job_context.h`, logging, status, and checked casts. They integrate with the same scheduler and versioning paths used by the larger compaction implementation: `VersionStorageInfo::ComputeCompactionScore()`, `EnqueuePendingCompaction()`, `MaybeScheduleFlushOrCompaction()`, `VersionSet::LogAndApply()`, and `InstallSuperVersionAndScheduleWork()`.

`PromoteL0()` is closely related to trivial move/refit logic in `db_impl_compaction_flush.cc`, but is narrower: it only promotes L0 to a higher empty level when L0 files are mutually non-overlapping and none are being compacted.

## Risks and Edge Cases

- `SuggestCompactRange()` only marks files in existing levels before the final non-empty level. If a range only overlaps the bottommost non-empty level, the function may mark nothing and still return OK.
- Marking files for compaction is advisory and can be delayed or ignored by later picker decisions if options, errors, pauses, or scheduling state prevent compaction.
- `PromoteL0()` assumes sorted L0 files are non-overlapping. This excludes common L0 states with overlapping flush outputs, so callers must only use it after constructing a compatible L0.
- `PromoteL0()` requires all levels up to the target to be empty. It will not merge with existing target-level files or compact through intermediate levels.
- The promotion is metadata-only. Incorrect overlap validation would create invalid leveled-LSM invariants without rewriting data, so the comparator checks and empty-level checks are correctness-critical.
- The code calls `job_context.Clean()` on early validation failures while still under the mutex even though the job context has not accumulated normal job work; this is harmless but shows the function is using shared cleanup idioms rather than a bespoke context.

## Test Signals

Tests should cover advisory marking and scheduling in `SuggestCompactRange()`, including null bounds, partial bounds, and no-overlap ranges. `PromoteL0()` needs tests for invalid target levels, target level out of range, files being compacted, overlapping L0 files, non-empty intermediate/target levels, successful manifest edits, and preservation of all file metadata fields during the L0-to-target move.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_impl/db_impl_experimental.cc -->
