# Research: sources/storage-engines/rocksdb/db/version_set.cc

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-008623`: lines 1-6776, `Docs/researches/chunks/subset-b-008623_research.md`
- `subset-b-008624`: lines 6777-8568, `Docs/researches/chunks/subset-b-008624_research.md`

## Chunk Research

### subset-b-008623: lines 1-6776

# sources/storage-engines/rocksdb/db/version_set.cc lines 1-6776

## Scope

This chunk covers the first 6,776 lines of RocksDB's `db/version_set.cc`. It implements the central in-memory and MANIFEST-facing version machinery for SST and blob-file metadata: file lookup helpers, point lookup and MultiGet file selection, level iterators over SSTs, table property/metadata APIs, blob value resolution, compaction scoring and file-priority bookkeeping, version lifetime management, and the first large part of `VersionSet` MANIFEST writer batching.

The chunk starts at includes and local read-path helpers and ends inside the public `VersionSet::LogAndApply()` overload after it validates multi-edit inputs. Later manifest recovery, manifest replay, full `LogAndApply()` wrapper control flow, WAL metadata helpers, and additional `VersionSet` utilities continue after this range and are intentionally out of scope for this chunk.

## Purpose

The code in this range maintains the immutable metadata view that readers, compactions, and recovery depend on:

- select the minimal set of SST files that might contain a key or key range;
- expose stable iterators over the current version's files, including range tombstone handling and MultiScan pruning;
- perform point lookups, MultiGet lookups, and blob-index materialization through table cache and blob source integration;
- expose table properties, column-family metadata, live-file metadata, live-size estimates, and debug summaries;
- compute compaction scores, compaction priorities, and special compaction candidate lists for TTL, periodic compaction, bottommost cleanup, forced blob GC, read-triggered compaction, and explicit table-property marks;
- prepare a `VersionStorageInfo` before it becomes current by deriving level briefs, file indexes, base-level byte targets, bottommost-file state, and file-location indexes;
- manage `Version` reference counts and obsolete file metadata transfer when old versions are released;
- batch and persist `VersionEdit`s through `VersionSet::ProcessManifestWrites()`, including atomic-group handling, manifest rotation, CURRENT-file installation, WAL metadata edits, and installing new `Version`s.

## Important APIs, Types, And Functions

- `FindFileInRange()`, public `FindFile()`, `AfterFile()`, `BeforeFile()`, and `SomeFileOverlapsRange()` are the low-level key-range predicates for sorted level files and unordered/overlapping L0 files.
- `MultiScanInternalKey()`, `MultiScanRangeOverlapsFile()`, `ForEachMultiScanOverlappingFile()`, and `GetMultiScanOverlappingFiles()` map bounded `MultiScanArgs` ranges to candidate SST file indexes, handling timestamp comparators by seeking with max timestamps.
- `DoGenerateLevelFilesBrief()` builds compact arena-backed `LevelFilesBrief` arrays from `FileMetaData`, copying encoded smallest/largest internal keys into contiguous arena storage.
- `FilePicker` is the single-key lookup planner. It walks levels from newest to oldest, uses `FileIndexer` fractional-cascading bounds for non-L0 levels, scans overlapping L0 files, and returns `FdWithKeyRange` candidates until no lower level can contain the key.
- `FilePickerMultiGet` extends the same idea for `MultiGetRange`, maintaining per-key search bounds, splitting a batch by file, skipping keys filtered out of a level, and preserving duplicate-key and key-spanning-next-file behavior.
- `LevelIterator` is an `InternalIterator` that lazily opens table iterators over non-overlapping level files. It supports seek/seek-for-prev/first/last/next/prev, table-cache iterator reuse, prepared MultiScan iterators, async prepare, lower/upper bound checks, sequential readahead state, pinned iterators, range tombstone iterators, and synthetic sentinel keys at file boundaries.
- `AddTableIteratorForLevel()`, `Version::AddIterators()`, `Version::AddIteratorsForLevel()`, and `Version::TEST_GetLevelIterator()` build child iterators for DB iterators. L0 gets one table iterator per file because files can overlap; lower levels usually get one `LevelIterator`.
- `Version::Get()`, `Version::MultiGet()`, coroutine-gated `Version::MultiGetAsync()`, and `Version::ProcessBatch()` implement SST-side point-read execution after memtables have been checked by higher layers.
- `Version::GetBlob()`, `Version::MultiGetBlob()`, `BlobFetcher`, `BlobIndex`, `BlobSource`, and `BlobFileMetaData` resolve integrated BlobDB blob references into user-visible values or wide-column default values.
- Table-property and metadata APIs include `GetTableProperties()`, `GetPropertiesOfAllTables()`, `GetPropertiesOfTablesInRange()`, `GetPropertiesOfTablesByLevel()`, `GetAggregatedTableProperties()`, `TablesRangeTombstoneSummary()`, `GetMemoryUsageByTableReaders()`, `GetColumnFamilyMetaData()`, `GetSstFilesSize()`, `GetSstFilesBoundaryKeys()`, and `GetCreationTimeOfOldestFile()`.
- `VersionStorageInfo` functions in this range include `PrepareForVersionAppend()`, `ComputeCompensatedSizes()`, `ComputeCompactionScore()`, `EstimateCompactionBytesNeeded()`, `UpdateFilesByCompactionPri()`, `CalculateBaseBytes()`, `GenerateLevelFilesBrief()`, `GenerateLevel0NonOverlapping()`, `GenerateBottommostFiles()`, `GenerateFileLocationIndex()`, `GetOverlappingInputs()`, `GetCleanInputsWithinInterval()`, `EstimateLiveDataSize()`, `RangeMightExistAfterSortedRun()`, `CalculateSSTWriteHint()`, and epoch recovery helpers.
- `VersionSet::ManifestWriter`, `AtomicGroupReadBuffer`, `VersionSet::VersionSet()`, `Close()`, `Reset()`, `UpdatedMutableDbOptions()`, `TuneMaxManifestFileSize()`, `AppendVersion()`, `ProcessManifestWrites()`, `WakeUpWaitingManifestWriters()`, and the start of `LogAndApply()` provide the manifest batching and version installation substrate.

## Control Flow

Point lookup flow starts in `Version::Get()`. A `GetContext` is constructed with comparator, merge operator, sequence/tombstone output pointers, optional blob fetcher, and tracing ID. `FilePicker` then returns potentially relevant SST files in newest-to-oldest semantic order. For each file, `table_cache_->Get()` searches the SST with level-specific filter skipping, histogram tracking, and sampled read accounting. The `GetContext` state controls whether lookup continues (`kNotFound`, `kMerge`) or returns immediately (`kFound`, `kDeleted`, corrupt states, unexpected blob index, merge-operator failure). If the final state is merge-in-progress after all files are exhausted, a full merge with no base value is attempted.

`MultiGet()` builds one `GetContext` per key, attaches those contexts to `MultiGetRange` entries, and then uses `FilePickerMultiGet` to group keys by current SST file. The synchronous path calls `MultiGetFromSST()` per file and dumps per-level index/filter/SST-read histograms. When coroutine support and async I/O are available, non-L0 work can batch multiple file tasks through `MultiGetFromSSTCoroutine()`, with `ProcessBatch()` splitting ranges into likely-in-level and leftover batches after filter checks. After SST reads, collected blob indexes are resolved in `MultiGetBlob()`, and remaining merge/not-found states are finalized per key.

Iterator construction distinguishes L0 from sorted lower levels. `Version::AddIteratorsForLevel()` adds each L0 file as an independent table iterator so overlap is merged by the parent. For levels greater than zero, it usually constructs one `LevelIterator` that binary-searches file ranges and lazily opens the relevant table iterator. With `MultiScanArgs`, the code first prunes to overlapping files; a single relevant lower-level file can use a direct table iterator, while multiple files use `LevelIterator` with per-file scan options.

`LevelIterator` seek flow finds the candidate file with `FindFile()`, initializes or reuses the file iterator through `InitFileIterator()`, seeks inside the table, handles async `TryAgain`, optionally stops at prefix exhaustion, creates range tombstone sentinel keys at file boundaries, and skips empty files forward/backward. Range tombstone integration is subtle: the parent merging iterator can observe sentinel keys so tombstone iterators remain alive across table-file transitions even when a file has no point keys.

Version preparation flow is `Version::PrepareAppend()` then `VersionStorageInfo::PrepareForVersionAppend()`. It may initialize bounded table-property stats, compute compensated file sizes, update the number of non-empty levels, calculate base-level target bytes, sort file priorities, generate file indexer and `LevelFilesBrief`, detect non-overlapping L0, compute bottommost files, and build a file-number to `(level, position)` index. `VersionSet::AppendVersion()` then computes compaction scores, finalizes the storage info, unrefs the old current version, sets the new current version, refs it, and links it into the CF's version list.

Manifest write flow is centered on `VersionSet::ProcessManifestWrites()`. The caller holds the DB mutex. The first queued `ManifestWriter` can group compatible subsequent writers, except column-family manipulation and no-manifest dummy edits. The function builds per-CF `VersionBuilder`s, applies `VersionEdit`s in memory via `LogAndApplyHelper()`, adjusts atomic-group `remaining_entries_` when dropped CF edits are skipped, saves builders into new `Version`s, and verifies atomic-group shape in debug builds. It then decides whether to rotate the MANIFEST, releases the DB mutex for table-handler loading and filesystem writes, optionally writes a new full-state MANIFEST snapshot, appends encoded edits, syncs, installs CURRENT for a new descriptor file, reacquires the mutex, applies WAL metadata edits, updates I/O status and quarantine state, installs new versions or CF add/drop effects, updates descriptor sequence/manifest numbers, and wakes grouped writers.

## State And Persistence Behavior

`Version` objects are immutable once finalized and ref-counted. Releasing the last reference unlinks the version and decrements every referenced `FileMetaData`; metadata with no remaining refs is moved to `VersionSet::obsolete_files_` with enough context for table-cache release and eventual deletion. Live versions therefore define the set of SST and blob files that must not be purged.

`VersionStorageInfo` owns per-level `FileMetaData*` vectors, blob file metadata, arena-backed file briefs, compaction-priority arrays, compaction scores, bottommost-file lists, file-location maps, accumulated stats, estimated pending compaction bytes, compact cursors, and epoch-number requirements. It copies some accounting from a previous storage info so stats and cursors persist across version transitions.

MANIFEST persistence is done by encoded `VersionEdit`s appended to `descriptor_log_`, with rotation when size exceeds the tuned threshold or no descriptor exists. New MANIFEST files are populated with current CF state and WAL additions before appending the current edit batch, then installed through `CURRENT`. On failures, new versions are deleted, the current descriptor is reset so the next update creates a fresh MANIFEST, and a newly created MANIFEST may be deleted only when the manifest I/O itself failed rather than when CURRENT installation had ambiguous remote-filesystem semantics.

Atomic manifest groups are represented by `VersionEdit::IsInAtomicGroup()` and `remaining_entries_`. `AtomicGroupReadBuffer` collects group entries during replay and rejects size mismatches or normal edits mixed into an unfinished group. `ProcessManifestWrites()` preserves group structure during batching and adjusts remaining counts if dropped-column-family edits are omitted.

Blob-file state is sorted by blob file number and stored alongside SST state. Blob reads validate that referenced blob file metadata exists and that the blob index is neither TTL nor inlined. Forced blob GC candidate computation uses blob-file garbage ratios and the linked SST set from the oldest eligible blob metadata to mark SST files for compaction.

Compaction state is derived, not directly persisted here, but it controls future persistent edits. Scores account for compaction style, L0 file count and size, dynamic base levels, FIFO size/TTL/temperature triggers, incoming downcompact bytes, unnecessary dynamic levels, and compensated deletion sizes. Candidate lists are populated for explicit marks, bottommost cleanup after snapshot advancement, TTL expiry, periodic compaction, forced blob GC, and read-triggered compaction.

Epoch-number recovery updates file metadata and CF epoch counters. If epoch numbers are missing or force recovery is requested, all files in each non-L0 level receive one epoch per level from bottom to top, while L0 files receive distinct epochs in reverse file order. In ingest-behind mode, the reserved ingest-behind epoch number is consumed first.

## Dependencies And Integration Points

This chunk is tied to many RocksDB subsystems:

- table access through `TableCache`, `TableReader`, `InternalIterator`, table properties, table open options, range tombstone iterators, and block-cache tracing;
- read semantics through `LookupKey`, `GetContext`, `MergeContext`, `MergeHelper`, merge operators, wide columns, snapshots, read callbacks, pinned iterators, and `ReadOptions` bounds/timestamps;
- compaction through `CompactionStyle`, `FileIndexer`, `CompactionPicker` priorities, compaction boundaries, file temperature age thresholds, FIFO options, TTL, periodic compaction, and read-triggered compaction sampling;
- blob storage through `BlobIndex`, `BlobSource`, `BlobFileMetaData`, blob read request batching, blob garbage metadata, and linked SST tracking;
- MANIFEST persistence through `VersionEdit`, `VersionBuilder`, `BaseReferencedVersionBuilder`, `log::Writer`, `WritableFileWriter`, descriptor/CURRENT filenames, `SyncManifest()`, and `SetCurrentFile()`;
- column families through `ColumnFamilyData`, `ColumnFamilySet`, mutable/immutable options, per-CF log numbers, full-history timestamp lows, table cache, internal stats, and file metadata cache reservation managers;
- filesystem and observability through `Env`, `FileSystem`, `FSDirectory`, file checksums, random/sequential file readers, event listeners, `IOStatus`, statistics tickers/histograms, perf context, sync points, and info logging.

Public-facing behavior supported by this file includes `DB::Get`, `MultiGet`, iterators, MultiScan, table-property APIs, column-family metadata APIs, approximate live-size/file-size introspection, compaction scheduling, manifest write durability, and obsolete-file protection.

## Risks And Edge Cases

- File range comparisons must consistently strip or preserve user-defined timestamps. MultiScan and file-overlap code compare without timestamps where appropriate but seeks use synthetic max-timestamp internal keys.
- L0 ordering and overlap are special. `FilePicker` and `FilePickerMultiGet` scan L0 files rather than relying on sorted disjoint ranges; treating L0 like lower levels can miss newer overlapping data.
- Fractional-cascading bounds from `FileIndexer` reduce lower-level search cost but must be reset when a level is empty, a key falls beyond the right bound, or a key is skipped for the next level.
- `LevelIterator` has three validity states: valid table key, invalid table iterator, and sentinel key. Mistakes around `to_return_sentinel_`, range tombstone iterator lifetime, or prefix exhaustion can hide tombstones or make iterators step across prefix boundaries incorrectly.
- Prepared MultiScan iterators are stored by file index and consumed on first `InitFileIterator()`. Reusing or leaking them would affect async scans and memory ownership.
- `Get()` may stop early when `max_covering_tombstone_seq` is set, because lower levels can only contain covered keys. Incorrect tombstone propagation would produce false not-found or stale value returns.
- Blob resolution converts blob indexes into values after SST lookup. Invalid blob file numbers, TTL/inlined blob indexes, `kBlockCacheTier` incomplete reads, and value-size soft-limit aborts all have separate status behavior.
- Compaction score scaling changes priority without changing the 1.0 trigger threshold. Dynamic-level score changes, L0-size boosting, unnecessary-level draining, FIFO temperature changes, and incoming downcompact bytes can interact in non-obvious ways.
- `ComputeCompensatedSizes()` mutates `FileMetaData` only when `compensated_file_size` is zero; changing this invariant could race with readers sharing file metadata.
- Bottommost compaction marking is gated by oldest snapshot sequence, optional delay, ingest-behind mode, and user-defined timestamp history low. Ignoring timestamp max checks can create futile or repeated compactions.
- Forced blob GC assumes blob files are ordered and that the oldest metadata has linked SSTs. Corrupt or stale blob-to-SST linkage would mark wrong SSTs for compaction.
- Manifest rotation has ambiguous failure cases on remote filesystems. The code intentionally keeps a newly written MANIFEST if CURRENT installation status is ambiguous, because deleting it could make a DB unrecoverable if the remote rename actually succeeded.
- `ProcessManifestWrites()` releases the DB mutex during file I/O after constructing in-memory state. Any new state captured before unlock, such as current CF log numbers and full-history timestamp lows for a new MANIFEST, must be complete and immutable enough for the write window.
- Dropped column families inside atomic groups require adjusting `remaining_entries_`; otherwise recovery would see a corrupted atomic group even though the omission is intentional.

## Test Signals

Expected coverage for this chunk should come from tests around:

- point lookup ordering across L0 and lower levels, merge operands, covering range tombstones, blob indexes, wide columns, and filter-skipping on bottommost hits;
- MultiGet batch splitting, duplicate keys, keys spanning file boundaries, coroutine async I/O, per-level read histograms, and soft value-size aborts;
- iterator seek/next/prev behavior across empty files, prefix exhaustion, lower/upper bounds, range tombstone sentinel keys, and `ignore_range_deletions`;
- MultiScan pruning with bounded ranges, timestamp comparators, L0 overlapping files, standalone range tombstone files, and async prepared iterators;
- table-property fallback reads when table cache returns `Incomplete`, range tombstone summary output, metadata APIs, memory usage by table readers, and blob file metadata reporting;
- compaction scoring for level, universal, FIFO, dynamic-level bytes, TTL, periodic compaction, file-temperature changes, read-triggered compaction, bottommost cleanup, and forced blob GC;
- version lifetime and obsolete-file cleanup under iterators/readers holding old versions;
- epoch-number recovery with missing epochs, forced restart, L0 ordering, non-L0 level grouping, and ingest-behind reserved epoch behavior;
- MANIFEST batching, atomic group replay, dropped-CF atomic groups, manifest rotation, CURRENT installation, manifest sync failures, WAL addition/deletion edits, no-manifest dummy edits, and callback/waiter wakeup behavior;
- close-time MANIFEST verification paths that read back descriptor records and rewrite or report corruption on validation failure.

### subset-b-008624: lines 6777-8568

# sources/storage-engines/rocksdb/db/version_set.cc lines 6777-8568

## Scope

This chunk covers the tail of `VersionSet` in `db/version_set.cc`: manifest writer queue handling after `LogAndApply`, helpers for preparing `VersionEdit`s, manifest writer construction/reuse, normal and best-efforts MANIFEST recovery, column-family listing, level-count reduction, live-file checksum export, manifest dumping, file-number and WAL-retention counters, full-state MANIFEST snapshot writing, approximate range-size estimation, live/obsolete file metadata enumeration, column-family creation, aggregate live-version size accounting, SST metadata verification, and `ReactiveVersionSet` manifest tailing for secondary/follower instances.

The code is persistence-heavy. It owns how MANIFEST contents become in-memory `Version` state, how new MANIFESTs are compacted from current state, how file/WAL/blob metadata survives reopen, and how secondary instances safely switch to a primary's current MANIFEST.

## Purpose

- Serialize manifest updates so only the queue head performs `ProcessManifestWrites`, while later writers can be grouped, awakened, or failed consistently.
- Normalize `VersionEdit` metadata before commit: next file number, previous log number, last sequence, max column family ID for drops, and WAL-only edits that do not build a new `Version`.
- Reuse an existing MANIFEST on open when `reuse_manifest_on_open` is safe, otherwise fall back to creating a fresh MANIFEST on the next write.
- Recover a `VersionSet` from the current MANIFEST, including DB ID, per-CF log numbers, file metadata, epoch numbers, and optional table-reader loading.
- Support best-efforts recovery by scanning available MANIFESTs newest-first and retaining the latest consistent point-in-time state when the latest full state is unavailable.
- Emit utility views over MANIFEST state: list column families, dump a MANIFEST, export live-file checksum data, enumerate live metadata, and retrieve metadata for a file number.
- Rebuild a compact MANIFEST snapshot containing DB ID, current WAL additions/deletions, column-family descriptors, SST/blob metadata, compact cursors, per-CF WAL state, history timestamp low-watermark, last sequence, and compacted MANIFEST size.
- Provide size and offset approximations over LSM key ranges for DB properties, range tombstone compensation, and compaction accounting.
- Construct compaction input iterators over L0 and non-L0 inputs, including range tombstone iterators and optional ephemeral table readers.
- Track obsolete SST/blob/MANIFEST files while protecting pending outputs from premature deletion.
- Tail and switch MANIFEST readers in `ReactiveVersionSet` for secondary/follower DBs.

## Important APIs, Types, And Functions

- `VersionSet::LogAndApply(...)` is the public multi-CF manifest update entry. In this chunk it validates grouped edits, creates `ManifestWriter` queue nodes, waits until the first local writer reaches the queue head, rejects updates for dropped CFs, invokes an optional `pre_cb`, and delegates to `ProcessManifestWrites`.
- `ManifestWriter` instances in `manifest_writers_` carry a CF pointer, edit list, condition variable, completion status, and completion callback. The queue serializes manifest writers under the DB mutex.
- `LogAndApplyCFHelper()` prepares column-family add/drop edits, including persisting `max_column_family` on drops so IDs are not reused after recovery.
- `LogAndApplyHelper()` prepares non-CF edits and applies them to a `VersionBuilder` unless the edit is WAL-only.
- `GetFileOptionsForManifestWrite()` and `CreateManifestWriter()` centralize MANIFEST file options, preallocation, checksum handoff classification, listener plumbing, and log block offset setup for fresh or reopened MANIFEST writers.
- `ReopenManifestForAppend()` implements the `reuse_manifest_on_open` path. It requires a known `manifest_last_valid_record_end_`, rejects best-efforts recovery, tail-size mismatches, direct writes, reopen failures, and reopened-size mismatches, and constructs `descriptor_log_` positioned at the existing file tail.
- `Recover()` reads `CURRENT`, opens the referenced MANIFEST through `SequentialFileReader` and `log::Reader`, replays it with `VersionEditHandler`, stores `manifest_file_size_`, recovers epoch numbers, logs recovered CF state, and optionally reopens the MANIFEST for append.
- `ManifestPicker`, `TryRecover()`, and `TryRecoverFromOneManifest()` implement best-efforts recovery over all descriptor files in reverse file-number order using `VersionEditHandlerPointInTime`.
- `RecoverEpochNumbers()` asks each initialized, non-dropped `ColumnFamilyData` to fill missing file epoch numbers and recover the next CF epoch counter.
- `ListColumnFamilies()` and `ListColumnFamiliesFromManifest()` parse MANIFEST records through `ListColumnFamiliesHandler` without constructing a full DB.
- `ReduceNumberOfLevels()` creates a temporary `VersionSet`, recovers the default CF, rewrites `VersionStorageInfo` level arrays when files can be collapsed into the new last level, updates file-location indexes, and persists the change with `LogAndApply`.
- `GetLiveFilesChecksumInfo()` walks current versions for all initialized, non-dropped CFs and inserts SST plus blob file checksum records into `FileChecksumList`.
- `DumpManifest()` first discovers CF names in the MANIFEST, merges them with supplied descriptors, then uses `DumpManifestHandler` to print verbose/hex/JSON decoded records.
- `MarkFileNumberUsed()` and `MarkMinLogNumberToKeep()` monotonically update recovered file-number and WAL-retention state.
- `WriteCurrentStateToManifest()` writes a compact snapshot to a `log::Writer`: DB ID, WAL additions, rolled-over WAL deletions, each live CF descriptor, all SST file metadata, compact cursors, blob file metadata and garbage, per-CF log number, default-CF min-log-to-keep, full-history timestamp low, last sequence, and approximate compacted MANIFEST size.
- `ApproximateSize()` and `ApproximateOffsetOf()` estimate bytes in key ranges by combining level metadata, `FindFileInRange`, file-size shortcuts, and table-cache `ApproximateOffsetOf`/`ApproximateSize`.
- `RemoveLiveFiles()` and `AddLiveFiles()` iterate all live `Version` nodes for each initialized CF, with a defensive fallback if `current()` is not linked into the version list.
- `MakeInputIterator()` builds the iterator set consumed by compaction: individual table iterators for L0 inputs and `LevelIterator`s for sorted non-L0 levels, then wraps them in `NewCompactionMergingIterator`.
- `GetMetadataForFile()` searches initialized current versions for a table file number and returns its level, `FileMetaData`, and owning CF.
- `GetLiveFilesMetaData()` populates public `LiveFileMetaData` fields from current SST metadata, including CF/path, bounds, sequence numbers, reads sampled, compaction state, entry/delete counts, blob ancestry, checksums, temperature, times, and epoch number.
- `GetObsoleteFiles()` drains obsolete SST/blob/MANIFEST queues, holding back files whose numbers are at or above `min_pending_output`.
- `CreateColumnFamily()` constructs a new `ColumnFamilyData`, dummy version list, current `Version`, memtable, and CF log number after a persisted CF-add edit commits.
- `GetNumLiveVersions()`, `GetTotalSstFilesSize()`, and `GetTotalBlobFileSize()` summarize version-list and unique-file storage usage.
- `VerifyFileMetadata()` compares on-disk SST size with MANIFEST metadata and, when configured, opens the table through `TableCache::FindTable()` so table-derived unique ID verification can run.
- `ReactiveVersionSet` overrides normal writable behavior. Its `Recover()`, `ReadAndApply()`, and `MaybeSwitchManifest()` use `ManifestTailer` and `log::FragmentBufferedReader` to replay primary MANIFEST updates and switch readers when `CURRENT` changes.

## Control Flow

`LogAndApply` starts with a mutex-held edit list. Empty updates return OK. Multi-edit batches are debug-checked to ensure they do not include CF manipulation or dummy no-write edits. It creates local `ManifestWriter` objects, appends their addresses to `manifest_writers_`, and waits until the first local writer is at the queue head. If an earlier grouped writer already completed this writer, it returns the completed status. Otherwise it counts undropped CFs, runs `pre_cb` only when this invocation has exclusive writer ownership, removes queued writers on early failure, signals the next queue head, or calls `ProcessManifestWrites`.

For ordinary recovery, `Recover` resolves `CURRENT` to a MANIFEST path, opens it for sequential reading, constructs a checksummed `log::Reader`, and lets `VersionEditHandler` replay all records into this `VersionSet`. On success it records the consumed reader offset as `manifest_file_size_`, copies the DB ID, runs `RecoverEpochNumbers`, and logs recovered file/log/CF state. If the DB is writable and `reuse_manifest_on_open` is enabled, it calls `ReopenManifestForAppend`; failure to reopen is intentionally converted into OK fallback in that helper so the next write rotates to a new MANIFEST.

Best-efforts recovery has a different flow. `ManifestPicker` parses file names in the DB directory, keeps descriptor files, sorts them by descending file number, and returns full paths one at a time. `TryRecover` attempts `TryRecoverFromOneManifest`, and after a failed attempt resets in-memory state before trying the next older MANIFEST. `TryRecoverFromOneManifest` uses `VersionEditHandlerPointInTime` with incomplete valid versions allowed and reports whether table files were missing.

`WriteCurrentStateToManifest` is invoked from the new-MANIFEST path in `ProcessManifestWrites` after current per-CF mutable state has been captured under the DB mutex. It does not hold the mutex itself. It writes standalone records in a careful order: DB ID first, WAL additions, a rolled-over WAL-deletion watermark, then per-CF descriptor and file-state records. It writes the compacted MANIFEST size record last because that estimate depends on the current writer file size.

`ApproximateSize` scans levels in `[start_level, end_level)`. L0 files are all treated as boundary candidates because they are not sorted. For sorted levels it binary-searches start and end files, sums full intermediate file sizes exactly, saves first/last boundary files, and either approximates boundary contribution as half the intersecting size when within the configured error margin or asks table readers for offsets.

`MakeInputIterator` allocates an array sized for the number of compaction input streams. L0 files get one table iterator each after optional start/end filtering based on user keys without timestamps. Non-L0 levels get one `LevelIterator` per input level. Range tombstone iterator ownership or pointer slots are tracked beside each child iterator so the final compaction merging iterator can see file-local tombstones.

`ReactiveVersionSet::MaybeSwitchManifest` checks `CURRENT` on every recover/read cycle. If the current reader already points at that MANIFEST, it keeps tailing. If not, it verifies the path exists, opens a new sequential file, replaces the fragment-buffered reader, logs the switch, and asks the existing tailer to prepare for a new MANIFEST. Races where the primary switches and deletes the old/new MANIFEST become `Status::TryAgain`.

## State And Persistence Behavior

- `next_file_number_`, `prev_log_number_`, `descriptor_last_sequence_`, `manifest_file_number_`, `manifest_file_size_`, `min_log_number_to_keep_`, and `column_family_set_->GetMaxColumnFamily()` are persisted or reconstructed through MANIFEST edits.
- CF drops persist `max_column_family` so recovery never reuses a previously allocated CF ID.
- `reuse_manifest_on_open` depends on `manifest_last_valid_record_end_`, which represents the exact byte offset consumed by the recovery reader. The reopened writer uses that offset for both `WritableFileWriter` size accounting and the `log::Writer` block offset, preventing record framing corruption after appending.
- `best_efforts_recovery` intentionally disables MANIFEST reuse because it rebuilds MANIFEST/CURRENT from salvaged state rather than trusting a possibly stale tail.
- New compacted MANIFEST snapshots include WAL addition state and a WAL-deletion watermark. This prevents a later WAL-addition record in the new MANIFEST from making an already-deleted WAL appear live again.
- SST metadata persistence is broad: file number, path ID, size, smallest/largest internal keys, sequence bounds, marked-for-compaction flag, temperature, blob ancestry, oldest ancestor/file creation times, epoch number, checksums, unique ID, range-deletion compensation, tail size, and user-defined timestamp metadata.
- Blob file metadata in the MANIFEST includes total blob count/bytes, checksum method/value, and garbage count/bytes when nonzero.
- Compact cursors and `full_history_ts_low` are written per CF, preserving compaction progress and history-trimming boundaries across reopen.
- `last_compacted_manifest_file_size_` and manifest tuning state are updated when a new descriptor log is installed and later used to tune maximum MANIFEST size.
- Obsolete SST/blob queues are drained only for numbers below `min_pending_output`, protecting files that may still be written or referenced by pending operations.
- `ReactiveVersionSet` is read-only with respect to normal `LogAndApply`; its persistent state arrives by replaying primary MANIFEST records.

## Dependencies And Integration Points

- MANIFEST IO uses `FileSystem`, `FSSequentialFile`, `FSWritableFile`, `SequentialFileReader`, `WritableFileWriter`, `log::Reader`, `log::FragmentBufferedReader`, and `log::Writer`.
- Version replay and printing depend on `VersionEditHandler`, `VersionEditHandlerPointInTime`, `ManifestTailer`, `ListColumnFamiliesHandler`, and `DumpManifestHandler`.
- Version construction depends on `ColumnFamilySet`, `ColumnFamilyData`, `Version`, `VersionBuilder`, `VersionStorageInfo`, `MutableCFOptions`, and `MutableCFState`.
- Table validation and approximation depend on `TableCache`, `TableReader`, `TableCacheOpenOptions`, `TableReaderCaller`, `InternalKeyComparator`, `FdWithKeyRange`, `LevelFilesBrief`, and `FindFileInRange`.
- Compaction iterator creation integrates with `Compaction`, `RangeDelAggregator`, `TruncatedRangeDelIterator`, `LevelIterator`, and `NewCompactionMergingIterator`.
- Public/admin surfaces include `DB::GetLiveFilesMetaData`, `DB::GetLiveFilesChecksumInfo`, `ldb` checksum/manifest commands, `ReduceNumberOfLevels`, and manifest dump tooling.
- Recovery/open integration is through `DBImpl::Open`, best-efforts recovery, read-only opens, secondary/follower implementations, and `CURRENT` file management.
- Observability and fault-injection rely on `ROCKS_LOG_*`, `TEST_SYNC_POINT`, `TEST_SYNC_POINT_CALLBACK`, and random kill points around MANIFEST writes.

## Risks And Edge Cases

- Manifest writer queue entries are addresses of local `ManifestWriter` objects. Correctness relies on all queued local writers being completed or removed before `LogAndApply` returns.
- `pre_cb` is intentionally delayed until the call owns the manifest writer slot; moving it earlier could execute side effects for work that later gets grouped or rejected.
- `ReopenManifestForAppend` returns OK on many fallback cases. Callers must interpret OK with `descriptor_log_ == nullptr` as "create a fresh MANIFEST later", not successful reuse.
- Appending to an existing MANIFEST is unsafe if physical size differs from the last valid record end, if direct writes remain enabled, or if the reopened handle reports a different size. These guards protect log record framing.
- `WriteCurrentStateToManifest` runs without the DB mutex. Its inputs must be stable snapshots captured before mutex release; adding new per-CF mutable fields needs the same treatment.
- The compacted MANIFEST snapshot record order matters for recovery interpretation and for the final compacted-size estimate.
- `ReduceNumberOfLevels` mutates internal `VersionStorageInfo` arrays and `file_locations_` directly, so it is only safe under its strict condition that at most one old high level contains files.
- `ApproximateSize` assumes internal key ordering and non-overlap properties for sorted levels. Range-boundary comparisons, timestamped comparators, or inclusive/exclusive mistakes can overcount or undercount.
- `MakeInputIterator` allocates raw iterator arrays and transfers tombstone iterator ownership into the merging iterator setup. Leaks or dangling tombstone pointers are plausible risks if constructor contracts change.
- `GetLiveFilesMetaData` falls back to the last CF path when a file path ID exceeds configured paths. That protects metadata generation but can mask inconsistent path IDs outside debug builds.
- `VerifyFileMetadata` only performs unique-ID verification when `verify_sst_unique_id_in_manifest` is enabled; size mismatch is always checked, but checksum verification is elsewhere.
- `ReactiveVersionSet::MaybeSwitchManifest` handles races by returning `TryAgain`, but non-POSIX filesystems may still require extra care because the primary can delete a MANIFEST while a secondary is opening or reading it.

## Test Signals

- `db_basic_test.cc` exercises `reuse_manifest_on_open`, including default-disabled behavior, reopening for append, block-offset/size accounting after reuse, close/recovery marker interactions, and fallback cases.
- `version_set_test.cc` covers best-efforts recovery through `TryRecover`/`TryRecoverFromOneManifest`, point-in-time recovery, atomic-group handling, and `ReactiveVersionSet` recover/read-and-apply behavior for valid, incomplete, corrupted, and incorrectly sized atomic groups.
- `db_secondary_test.cc` uses the `ReactiveVersionSet::MaybeSwitchManifest` sync points to test races while a secondary observes `CURRENT` and switches MANIFESTs.
- `external_sst_file_basic_test.cc`, `db_compaction_test.cc`, and `compaction_service_test.cc` observe `VersionSet::MakeInputIterator:NewCompactionMergingIterator`, especially around compaction input counts and external/remote compaction paths.
- `db_range_del_test.cc` exercises `VersionSet::ApproximateSize` for compensated range tombstone sizes, including assertions around valid start/end ordering.
- `db_etc2_test.cc` and `ldb_cmd_test.cc` validate live-file checksum extraction from MANIFEST state through `GetLiveFilesChecksumInfo`.
- SST unique-ID recovery tests route through `VersionEditHandlerPointInTime::VerifyFile()` into `VersionSet::VerifyFileMetadata`, checking both mismatch corruption and backward-compatible missing-ID behavior.
- Useful failure signatures in this chunk include manifest corruption on reopen, file-number reuse, lost CF IDs after drop/recreate, WAL deletion/addition inconsistencies after MANIFEST rotation, stale or missing live-file checksum data, compaction iterator input-count mismatches, secondary `TryAgain` loops, and incorrect live/obsolete file deletion decisions.
