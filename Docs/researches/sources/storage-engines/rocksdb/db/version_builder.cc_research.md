# sources/storage-engines/rocksdb/db/version_builder.cc

## Purpose

`version_builder.cc` implements `VersionBuilder`, the accumulator that applies a sequence of `VersionEdit`s to a base `VersionStorageInfo` and materializes a new storage view without constructing full intermediate versions. It handles SST additions/deletions, blob-file metadata deltas, compact cursors, consistency checks, table-reader preloading, point-in-time recovery tracking, savepoints, and base-version lifetime management.

## Important APIs, Types, and Functions

Most behavior lives in `VersionBuilder::Rep`. Comparators sort L0 by newest sequence or epoch and non-L0 by smallest key. `LevelState` tracks deleted and newly added files per level. `BlobFileMetaDataDelta` and `MutableBlobFileMetaData` accumulate garbage and SST link changes. Important methods include `Apply`, `ApplyFileAddition`, `ApplyFileDeletion`, `ApplyBlobFileAddition`, `ApplyBlobFileGarbage`, `SaveTo`, `SaveSSTFilesTo`, `SaveBlobFilesTo`, `CheckConsistencyDetails`, `ValidVersionAvailable`, `OnlyMissingL0Suffix`, `LoadTableHandlers`, and savepoint wrappers. `BaseReferencedVersionBuilder` refs/unrefs the base version around builder use.

## Control Flow

`Apply` first checks base consistency, processes blob additions and garbage, then table deletions, table additions, and compact cursors. Table-file level tracking prevents adding an already-live file or deleting from the wrong level. Deleting an added file unrefs its temporary metadata and may record intermediate files for cleanup in point-in-time mode. Saving merges base files with unordered additions, filters deletions and missing L0 files, sorts by the level's required comparator, merges blob metadata from base and mutable state, writes compact cursors, and reruns consistency checks. `LoadTableHandlers` opportunistically opens newly added files subject to cache capacity and initial-load limits.

## State and Persistence Behavior

The builder owns temporary `FileMetaData` refs for added files and releases pinned table readers/cache reservations when refs drop to zero. It does not write MANIFEST records itself; it consumes edits already decoded from MANIFEST/WAL-like metadata and populates `VersionStorageInfo`. Blob metadata deleters mark obsolete blob files in `VersionSet` and evict blob cache entries. Point-in-time mode tracks found, missing L0/non-L0 SSTs, missing blob files, atomic-group edits, and intermediate files so recovery can accept a complete version or, when configured, an older valid view missing only an L0 suffix and associated blobs.

## Dependencies and Integration Points

Dependencies include blob metadata/cache, cache reservation manager, table cache, internal stats, version edit/handler/set/storage, version utilities, sync points, and string utilities. The class is used by manifest application, DB open/recovery, secondary/tailing version handling, and table-reader warmup. It cooperates with `ColumnFamilyData` for options, table cache, blob cache, and file metadata cache reservations.

## Risks and Test Signals

Risks are high: refcount imbalance can leak or prematurely free file metadata/readers; level/order checks must preserve L0 epoch and non-L0 non-overlap invariants; blob-to-SST links must remain bidirectionally consistent; memory reservation failure must unwind added metadata; incomplete-version recovery must not expose non-suffix missing data; and invalid levels during `num_levels` shrink must cancel out. Tests should cover add/delete reorderings, duplicate file numbers, wrong-level deletes, L0 ordering with and without epoch numbers, non-L0 overlap corruption, blob garbage overflow, link consistency, missing-file PIT recovery, savepoint copy/ref behavior, cache-reservation limits, table handler load limits, and obsolete blob cleanup.
