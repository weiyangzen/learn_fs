# sources/storage-engines/rocksdb/db/version_set.h

## Purpose

`version_set.h` declares the central RocksDB metadata model for DB versions, column-family version state, MANIFEST persistence, live-file accounting, and point/range read integration over SST and blob files. The header sits on the critical boundary between LSM metadata management and the DB read/write/compaction subsystems.

At the storage layer, a `Version` is a point-in-time view of one column family's table files and blob files. A `VersionStorageInfo` owns the per-level file layout and derived indexes used for reads and compaction picking. A `VersionSet` owns all column-family versions for a DB, writes and recovers MANIFEST edits, allocates file and sequence numbers, tracks live and obsolete files, and exposes helper APIs for compaction, metadata, backup/checksum, approximate-size, and recovery flows.

The file is mostly declarations and inline guards, but it defines the public contract that `version_set.cc`, `version_builder`, `column_family`, `DBImpl`, compaction picker/job code, table cache, blob storage, and secondary/read-only recovery paths rely on.

## Important APIs, Types, and Functions

Top-level helpers provide key-range search primitives over sorted SST metadata:

- `FindFile()` returns the first file whose largest internal key is greater than or equal to a search key.
- `SomeFileOverlapsRange()` checks whether a level's files overlap a user-key interval, with optimized handling for disjoint sorted files.
- `DoGenerateLevelFilesBrief()` builds compact `LevelFilesBrief` structures from full `FileMetaData` vectors.
- `EpochNumberRequirement` records whether SST epoch numbers may be absent or must be present.
- `VersionEditParams` aliases `VersionEdit` for call sites that carry edit fields as parameters without intending to represent a valid MANIFEST record.

`VersionStorageInfo` is the main per-version layout container. It stores `files_` by level, sorted `blob_files_`, per-level briefs, a `FileIndexer`, file-number-to-location lookup, compaction-priority ordering, compaction scores and levels, round-robin compaction cursors, base-level/dynamic-level sizing state, accumulated table statistics, bottommost-file state, periodic/TTL/read-triggered/blob-GC compaction candidates, and epoch-number policy. Important methods include `AddFile()`, `AddBlobFile()`, `PrepareForVersionAppend()`, `SetFinalized()`, `ComputeCompactionScore()`, `EstimateCompactionBytesNeeded()`, `GetOverlappingInputs()`, `OverlapInLevel()`, `RecoverEpochNumbers()`, `GetFileMetaDataByNumber()`, `GetBlobFileMetaData()`, `GetBlobStats()`, `FilesMarkedForCompaction()`, `BottommostFilesMarkedForCompaction()`, `RangeMightExistAfterSortedRun()`, `MaxBytesForLevel()`, `EstimateLiveDataSize()`, and `CalculateSSTWriteHint()`.

`VersionStorageInfo::FileLocation` is a compact `(level, position)` handle for file-number lookups. `GetFileLocation()` validates the indexed location against `files_`, making the generated location map a guarded fast path for table metadata lookup.

`ObsoleteFileInfo` and `ObsoleteBlobFileInfo` represent deletion candidates after versions release references. `ObsoleteFileInfo` owns a `FileMetaData*`, path, uncache aggressiveness, a `only_delete_metadata` flag for trivial-move/shared-file cases, and optional cache-reservation release logic in `DeleteMetadata()`.

`Version` represents one column-family version. It exposes read path methods (`AddIterators()`, `AddIteratorsForLevel()`, `Get()`, `MultiGet()`, `GetBlob()`, `MultiGetBlob()`), metadata/property APIs (`GetTableProperties()`, `GetPropertiesOfAllTables()`, `GetPropertiesOfTablesInRange()`, `GetAggregatedTableProperties()`, `TablesRangeTombstoneSummary()`), lifecycle methods (`PrepareAppend()`, `Ref()`, `Unref()`), live-file accounting (`AddLiveFiles()`, `RemoveLiveFiles()`), user-facing metadata builders (`GetColumnFamilyMetaData()`, `GetSstFilesBoundaryKeys()`, `GetCreationTimeOfOldestFile()`), and test hooks. It owns a `VersionStorageInfo`, links into a per-CF version list, and caches option/table/blob/merge/operator dependencies needed by reads.

`AtomicGroupReadBuffer` buffers `VersionEdit`s belonging to an atomic group during MANIFEST replay. It tracks how many edits in the group have been read and exposes `AddEdit()`, `Clear()`, `IsFull()`, `IsEmpty()`, and the replay buffer.

`VersionSet` is the DB-wide manager. Key APIs include:

- `LogAndApply()` overloads for one edit, a batch for one column family, and batches across multiple column families. These persist edits to MANIFEST and install new current versions.
- `Recover()`, `TryRecover()`, `TryRecoverFromOneManifest()`, `ListColumnFamilies()`, `ReduceNumberOfLevels()`, `DumpManifest()`, and `RecoverEpochNumbers()` for startup, best-effort recovery, manifest inspection, and migration-style operations.
- File/sequence-number state: `NewFileNumber()`, `FetchAddFileNumber()`, `MarkFileNumberUsed()`, `LastSequence()`, `SetLastSequence()`, `LastAllocatedSequence()`, `SetLastAllocatedSequence()`, `FetchAddLastAllocatedSequence()`, `LastPublishedSequence()`, `SetLastPublishedSequence()`, and `SyncLastSequenceWithAllocated()`.
- WAL and manifest accounting: `MarkMinLogNumberToKeep()`, `MinLogNumberWithUnflushedData()`, `PreComputeMinLogNumberWithUnflushedData()` variants, `manifest_file_number()`, `manifest_file_size()`, `pending_manifest_file_number()`, and `io_status()`.
- Compaction/read helpers: `MakeInputIterator()`, `ApproximateSize()`, protected `ApproximateOffsetOf()`, and protected file-level `ApproximateSize()`.
- Live/dead metadata: `AddLiveFiles()`, `RemoveLiveFiles()`, `GetMetadataForFile()`, `GetLiveFilesMetaData()`, `GetLiveFilesChecksumInfo()`, `AddObsoleteBlobFile()`, `GetObsoleteFiles()`, and `GetObsoleteSstFilesSize()`.
- Column-family access and option integration: `GetColumnFamilySet()`, timestamp-size maps, `GetRefedColumnFamilySet()`, `UpdatedMutableDbOptions()`, `ChangeOffpeakTimeOption()`, and DB/file option accessors.

`ReactiveVersionSet` derives from `VersionSet` for secondary/reactive users that replay MANIFEST changes instead of writing them. It adds `ReadAndApply()`, a reactive `Recover()` over a fragment-buffered manifest reader, `ApplyOneVersionEditToBuilder()`, `MaybeSwitchManifest()`, and overrides `LogAndApply()` privately to return `NotSupported`.

## Control Flow and State Behavior

New versions are built by applying `VersionEdit`s through `VersionBuilder` and then calling `PrepareAppend()`/`PrepareForVersionAppend()` before appending the version. Preparation populates derived structures such as level briefs, file indexes, bottommost file lists, file-location maps, non-empty level counts, compaction-priority order, and accumulated table stats. Many accessors assert `finalized_`, so callers must respect the prepare/finalize sequence before exposing a `Version`.

Read flow enters `Version::Get()`, `MultiGet()`, iterator construction, or blob access. These methods use `VersionStorageInfo`'s level layout and file indexer to find candidate SSTs, use `TableCache` to read SST data, use `RangeDelAggregator`/tombstone state where needed, and resolve blob indexes through `BlobSource` when values are stored externally. Reads deliberately require no DB mutex for point lookup, relying on version reference counts to keep metadata stable while iterators or reads are live.

Compaction selection flow depends on `VersionStorageInfo::ComputeCompactionScore()`. That computes per-level scores, base-level sizing, estimated compaction debt, L0 delay trigger counts, and candidate lists for explicit marks, TTL expiration, periodic compaction, bottommost compaction, forced blob GC, and read-triggered compaction. The comments repeatedly require the DB mutex for candidate access and snapshot-sensitive recomputation. `UpdateOldestSnapshot()` recomputes bottommost-file eligibility as snapshots are released.

MANIFEST mutation flow goes through `VersionSet::LogAndApply()`. The overloads normalize one or many `VersionEdit`s into CF/edit lists and delegate to the virtual multi-CF implementation. Internally, the implementation uses manifest writer queues, `ProcessManifestWrites()`, `WriteCurrentStateToManifest()`, optional fresh MANIFEST creation, `CreateManifestWriter()`, and `AppendVersion()` to make edits durable before installing versions. It may release and reacquire the DB mutex while doing file I/O, so the header documents mutex requirements and callback slots around manifest writes.

Recovery flow reconstructs column families and current versions from MANIFEST files. Normal recovery uses the latest descriptor, while best-effort recovery can walk older MANIFESTs and retain the most recent consistent point-in-time version. `AtomicGroupReadBuffer` helps preserve atomic-edit group semantics. Secondary/reactive recovery uses `ReactiveVersionSet` and `ManifestTailer` to read and apply new edits, including manifest switching, without supporting local `LogAndApply()`.

Sequence-number flow distinguishes visible, allocated, and published sequence numbers. `last_sequence_` is what reads can see, `last_allocated_sequence_` matters when two write queues allocate WAL sequence numbers before publish, and `last_published_sequence_` tracks reader publication when publish sequence differs. `SyncLastSequenceWithAllocated()` is an explicit recovery repair hook to avoid creating new WAL/memtable state below an already allocated sequence after an error.

File-number and WAL retention flow is similarly centralized. `next_file_number_` allocates monotonically increasing file numbers; `MarkFileNumberUsed()` advances it during recovery/repair; `min_log_number_to_keep_`, per-CF log numbers, and `PreComputeMinLogNumberWithUnflushedData()` determine what WAL files can be ignored or deleted.

## State and Persistence Behavior

Persistent state represented here includes MANIFEST records, current file numbers, sequence numbers, column-family IDs and options metadata, table file metadata, blob file metadata, per-file checksums, WAL retention thresholds, and options/manifest file numbers. The header keeps a sharp distinction between durable descriptor state and in-memory derived indexes.

`VersionStorageInfo` owns memory-only acceleration structures: `LevelFilesBrief`, `FileIndexer`, `file_locations_`, compaction-priority indexes, bottommost lists, and accumulated statistics. These must be regenerated from persisted file metadata when recovering or building a new version. Bugs in regeneration do not directly corrupt the MANIFEST, but they can cause wrong read pruning, missed compaction, bad file deletion, or invalid metadata reporting.

`Version` reference counting is the in-memory persistence mechanism for snapshots and iterators. Older versions can stay alive after a newer current version is installed, preventing table/blob files from being deleted while live reads still reference them. `AddLiveFiles()` and `RemoveLiveFiles()` use all live versions to filter obsolete candidates before physical deletion.

MANIFEST state has several durability knobs: current and pending manifest file numbers, descriptor log writer, manifest size, last valid record end, last compacted manifest size, auto-tuned max manifest size, preallocation size, and close-time verification. `ReopenManifestForAppend()` distinguishes physical file size from the end of the last valid logical record to avoid appending after tolerated tail garbage.

Blob files are part of version state alongside SST files. `blob_files_` is sorted by blob file number, supports lower-bound metadata lookup, contributes to live-file lists, and provides garbage/space-amplification stats used by blob GC decisions.

Epoch numbers are tracked per file and per CF. `RecoverEpochNumbers()` can reset missing file epochs from the column-family epoch or update the CF with the maximum file epoch. This is a recovery-time consistency repair path for installations that encounter older or incomplete metadata.

## Dependencies and Integration Points

This header integrates with most major RocksDB DB internals:

- Metadata and persistence: `VersionEdit`, `VersionBuilder`, MANIFEST `log::Writer`/`log::Reader`, `ColumnFamilySet`, `ColumnFamilyData`, file naming, file checksums, and DB/options metadata.
- Read path: `TableCache`, `TableReader`, `GetContext`, `MultiGetContext`, `LookupKey`, `MergeContext`, `MergeIteratorBuilder`, range deletion aggregation, pinned iterators, read callbacks, and table properties.
- Compaction path: `Compaction`, `CompactionPicker`, compaction styles, write controller, off-peak options, file-size and overlap calculations, bottommost-file logic, TTL/periodic/read-triggered/forced-blob-GC candidates, and compaction input iterators.
- Blob path: `BlobFileMetaData`, `BlobIndex`, `BlobSource`, blob read contexts, and blob garbage accounting.
- Environment/storage: `Env`, `FileSystem`, `FSDirectory`, `FileOptions`, `SystemClock`, `IOStatus`, file-system tracing, cache reservation, and block-cache tracing.
- Concurrency and diagnostics: `InstrumentedMutex`, atomics, `Statistics`, `Logger`, `IOTracer`, `SyncPoint`-visible test hooks, and internal test helpers.
- Optional coroutine support: `DECLARE_SYNC_AND_ASYNC` for `Version::MultiGetFromSST` and coroutine-only declarations for async multiget batching.

The most important external consumers are `DBImpl` for writes/recovery/cleanup, read APIs for point and iterator lookup, compaction picker/job code for scoring and input iteration, backup/checkpoint/live-file APIs, secondary DBs through `ReactiveVersionSet`, and tests that inspect version state through `TEST_` hooks and DB properties.

## Risks and Edge Cases

Many methods depend on strict mutex and lifecycle preconditions. Accessing compaction candidate vectors without the DB mutex, reading `VersionStorageInfo` before finalization, or modifying versions without respecting reference counts can create subtle use-after-free, missed compaction, or file-deletion bugs.

The file-location index and level briefs are derived from `files_`. If file ordering differs from the assumptions (L0 by decreasing epoch/newest first; lower levels sorted by non-overlapping key ranges), `FindFile()`, overlap checks, file index pruning, and `GetFileMetaDataByNumber()` can return wrong candidates.

Bottommost-file marking is snapshot-sensitive and timestamp-sensitive. Incorrect `oldest_snapshot_seqnum_`, `full_history_ts_low`, range-tombstone thresholds, or ingest-behind handling can compact away versions/timestamps that should remain visible, or leave compaction debt unaddressed.

Sequence-number handling is high risk with `two_write_queues`. The header explicitly calls out recovery corruption if allocated-but-unpublished sequence numbers are ignored. Changes to write recovery must preserve the `last_sequence_ <= last_published_sequence_ <= last_allocated_sequence_` style invariants documented here.

MANIFEST append/reuse is sensitive to partial records, tail garbage, preallocation, rotation, writer queue wakeups, and DB mutex release windows. A bug can leave durable state ahead of in-memory state, in-memory state ahead of durable state, or append new edits after corrupted bytes.

Obsolete-file cleanup must account for live old versions, blob files, trivial moves with shared physical files, pending outputs, cache reservations, and shutdown state. Over-deletion risks data loss; under-deletion leaks disk/cache memory.

Best-effort recovery and reactive/secondary replay intentionally tolerate more states than normal writable recovery. They need to detect missing files, manifest switches, atomic groups, and dropped CFs without installing inconsistent versions.

## Test Signals

Relevant test signals are broad because this header defines shared infrastructure. Strong coverage comes from RocksDB DB, version, compaction, recovery, and blob tests that assert:

- Point reads, iterators, and `MultiGet` return correct values across flushes, compactions, snapshots, range tombstones, blob values, and table-cache states.
- Compaction scores, base levels, L0 delay triggers, bottommost files, TTL/periodic/read-triggered/blob-GC candidates, and overlap calculations match expected DB properties and compaction picker choices.
- MANIFEST recovery, dump/list-column-family APIs, best-effort recovery, manifest reuse, atomic-group replay, and secondary/reactive replay reconstruct consistent versions.
- File-number, WAL-retention, and sequence-number monotonicity survive normal writes, recovery, repair, two-write-queue errors, and restart.
- Live-file and obsolete-file APIs do not delete files referenced by old versions, snapshots, blob metadata, or pending outputs, while eventually reporting reclaimable SST/blob/manifest files.
- Table properties, aggregated properties, range tombstone summaries, live-file metadata, checksum metadata, approximate size, and column-family metadata reflect the current version state.

Targeted `TEST_` hooks in the header indicate additional unit signals around references, synthetic version append, estimated compaction debt, compaction candidate insertion, manifest tuning parameters, and atomic group replay counts.
