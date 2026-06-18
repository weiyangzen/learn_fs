# sources/storage-engines/rocksdb/db/column_family.cc

## Purpose

`column_family.cc` implements RocksDB's column-family metadata layer. It turns the declarations from `column_family.h` into the runtime machinery that owns column-family handles, validates and sanitizes column-family options, manages `ColumnFamilyData` lifetimes, installs `SuperVersion` snapshots, tracks write-stall state, delegates compaction picking, creates data directories, and maintains the `ColumnFamilySet` registry.

This file is central to DB open/recovery, write-path routing, read-path snapshot stability, flush/compaction scheduling, dynamic option updates, and column-family drop cleanup. It does not itself write MANIFEST records, SST files, or WAL records, but its state is the in-memory authority consumed by `VersionSet`, `DBImpl`, memtables, compaction pickers, table/blob caches, and write throttling.

## Important APIs, Types, and Functions

Handle and utility implementations:

- `ColumnFamilyHandleImpl` refs a `ColumnFamilyData` on construction, exposes ID/name/descriptor/comparator accessors, notifies listeners on deletion, unrefs the CFD under the DB mutex, and asks `DBImpl` to find/purge obsolete files if the last dropped handle was released.
- `GetColumnFamilyID`, `GetColumnFamilyUserComparator`, and `GetImmutableOptions` are narrow helper adapters from public `ColumnFamilyHandle*` to internal metadata.
- `ColumnFamilyHandleInternal` is implemented via the base handle behavior plus a mutable internal CFD pointer declared in the header; it is used by write-batch/memtable-inserter paths without incrementing CFD refcounts.

Option support functions:

- `CheckCompressionSupportedWithManager` verifies compression types through an optional `CompressionManager` or the built-in compression registry.
- `CheckCompressionSupported` checks per-level compression, default compression, zstd dictionary training/finalization support, nonzero dictionary-size limits, and blob compression availability.
- `CheckConcurrentWritesSupported` rejects in-place updates and memtable factories that do not support concurrent insertion when concurrent memtable writes are enabled.
- `CheckCFPathsSupported` rejects multiple CF/DB paths for compaction styles other than level and universal.
- `SanitizeCfOptions` clamps and derives mutable settings such as write buffer size, arena block size, min/max write buffers, number of levels, L0 thresholds, pending-compaction byte limits, TTL, periodic compaction, blob direct-write partitions, read-only flush triggers, and DB/CF path cleanup.
- `ColumnFamilyData::ValidateOptions` performs hard compatibility checks for compression, concurrent writes, unordered writes, CF paths, TTL/periodic-compaction table format, blob direct-write restrictions, user-defined timestamp restrictions, blob GC thresholds, read-triggered compaction threshold, FIFO constraints, async file open constraints, per-key protection sizes, FIFO temperature thresholds, and universal compaction read amplification.
- `ColumnFamilyData::SetOptions` parses a mutable-options-only map, validates the resulting options, then refreshes `mutable_cf_options_` derived settings.

`SuperVersion` implementation:

- `SuperVersion::Ref` and `SuperVersion::Unref` maintain atomic references.
- `SuperVersion::Init` captures `ColumnFamilyData`, mutable memtable, immutable memtable-list version, `Version`, `full_history_ts_low`, and the optional `SeqnoToTimeMapping`; it refs all pinned objects.
- `SuperVersion::Cleanup` unrefs immutable memtables, mutable memtable, current version, and CFD, and records memtables to delete after cleanup.
- `SuperVersionUnrefHandle` is the thread-local cleanup callback and intentionally cannot run full `SuperVersion` cleanup because it may be called under the `ThreadLocalPtr` mutex.

`ColumnFamilyData` implementation:

- The constructor sanitizes options, builds immutable/mutable CF options, registers DB paths, creates internal table property collectors, internal stats, table cache, blob file cache/source, the proper compaction picker, optional file-metadata cache reservation manager, and initial write-stall state.
- The destructor removes the CFD from the live linked list and registry if needed, unrefs current versions, destroys memtables and immutable memtable list state, asserts it is not queued for flush/compaction, and unregisters DB paths.
- `UnrefAndTryDelete` owns the tricky deletion path: it deletes the CFD when the last external reference is gone, or tears down `super_version_` and thread-local superversions when only the current superversion still holds the CFD.
- `SetDropped` marks non-default CFs as dropped, releases write-controller tokens, and removes the CF from `ColumnFamilySet`.
- `OldestLogToKeep` returns the CF log number, possibly lowered to include prepared transactions still present in mutable or immutable memtables when two-phase commit is enabled.
- `ConstructNewMemtable` and `CreateNewMemtable` allocate and install a new mutable memtable, assign IDs through `SetMemtable`, and respect latest mutable options.
- `NeedsCompaction`, `PickCompaction`, `RangeOverlapWithCompaction`, and `CompactRange` are compaction picker delegation points that pass current `VersionStorageInfo`, snapshots, timestamp history low watermarks, and manual range parameters.
- `RangesOverlapWithMemtables` builds a merging iterator over mutable and immutable memtables plus a range tombstone aggregator to detect unflushed overlap with user-key ranges.
- `GetReferencedSuperVersion`, `GetThreadLocalSuperVersion`, `ReturnThreadLocalSuperVersion`, `InstallSuperVersion`, and `ResetThreadLocalSuperVersions` implement the fast read-path superversion cache and the safe replacement path under the DB mutex.
- `AddDirectories` creates or reuses `FSDirectory` handles for each CF path using a caller-provided map to avoid duplicate directory objects.
- `SetFlushSkipReschedule`, `GetAndClearFlushSkipReschedule`, and `ShouldPostponeFlushToRetainUDT` implement the user-defined timestamp in-memtable-only flush postponement policy.
- `RecoverEpochNumbers` delegates epoch recovery to `VersionStorageInfo`.

Write-stall and compaction-pressure helpers:

- `GetWriteStallConditionAndCause` classifies normal, delayed, and stopped writes from unflushed memtables, L0 delay-trigger count, pending compaction bytes, and mutable/immutable CF options.
- `SetupDelay` adjusts delayed write rates using `WriteController`, previous compaction debt, near-stop/stopped penalties, and auto-compaction-disabled behavior.
- `RecalculateWriteStallConditions` obtains stop/delay/compaction-pressure tokens, logs state transitions, updates internal stats counters, rewards recovery from delay by increasing the delayed write rate, and maintains `prev_compaction_needed_bytes_`.
- `GetL0FileCountForCompactionSpeedup`, `GetPendingCompactionBytesForCompactionSpeedup`, and `GetMarkedFileCountForCompactionSpeedup` compute non-stall pressure signals for increasing compaction threads.

`ColumnFamilySet` and write-batch lookup:

- `ColumnFamilySet` constructs a dummy circular-list CFD, owns maps from name and ID to `ColumnFamilyData`, tracks timestamp-size maps, and caches the default CF pointer.
- `CreateColumnFamily` constructs a new CFD, inserts it into maps and the circular linked list, records timestamp sizes, updates the maximum CF ID, and populates the default cache for ID 0.
- `RemoveColumnFamily` removes ID/name/timestamp entries but does not directly unlink the CFD from the circular list; the destructor handles list unlinking.
- `ColumnFamilyMemTablesImpl::Seek` selects a CFD by column-family ID, fast-paths ID 0, and updates an internal handle for write-batch callbacks. Its `GetLogNumber`, `GetMemTable`, and `GetColumnFamilyHandle` return metadata for the selected CF.

## Control Flow

Column-family creation generally flows through `VersionSet::LogAndApply`, recovery, or manifest dumping into `ColumnFamilySet::CreateColumnFamily`. Creation constructs `ColumnFamilyData`, sanitizes options, initializes caches and compaction picker state, inserts the object into registry maps, and links it into the set's circular list. Later DB code installs memtables/current versions and calls `InstallSuperVersion` to publish a readable LSM view.

Reads take a fast path through `ColumnFamilyData::GetThreadLocalSuperVersion`: the thread swaps the TLS slot to `kSVInUse`; if it finds a current cached `SuperVersion`, it can avoid the DB mutex. If a background install scraped the slot to `kSVObsolete`, the read path locks the DB mutex, refs `super_version_`, and proceeds. Returning the SV uses compare-and-swap; a scrape during the read causes the caller to drop its obsolete cached reference instead of returning it to TLS.

Superversion installation is DB-mutex protected. `InstallSuperVersion` creates the new snapshot from current mem/imm/version pointers, shares or installs a sequence-number-to-time mapping, recomputes write-stall state only when mem/imm/current changed, scrapes all thread-local cached superversions before unrefing the old current superversion, pushes write-stall notifications on transitions, queues old superversions for deferred free, and increments `super_version_number_`.

Write-stall recalculation reads the current version storage's L0 delay-trigger count and pending compaction bytes. It first handles hard stop cases, then delayed cases, then normal pressure cases that ask the write controller for a compaction-pressure token. The result is stored in the installed `SuperVersion` so read/write callers can observe the CF's current stall condition.

Compaction selection is deliberately thin in this file. `NeedsCompaction` checks whether auto-compaction is enabled and asks the configured picker. `PickCompaction` and `CompactRange` pass current storage, options, snapshots, range bounds, and UDT trimming state into the picker and finalize selected input info against the current version before returning the `Compaction`.

Drop and destruction are split. `SetDropped` only marks the CF, removes it from the registry, and disables write-control tokens; client handles and old superversions can still keep data alive for reads. When references finally drain through `ColumnFamilyHandleImpl::~ColumnFamilyHandleImpl` and `ColumnFamilyData::UnrefAndTryDelete`, obsolete file discovery/purge is triggered for dropped CFs and the CFD tears down its memtables, versions, caches, and paths.

## State and Persistence Behavior

The file manages in-memory state with persistence implications:

- `log_number_` and `OldestLogToKeep` determine which WALs must remain recoverable for the CF, including prepared transaction sections in 2PC mode.
- `ColumnFamilyOptions` are sanitized and validated here before they become `ImmutableOptions`, `MutableCFOptions`, compaction picker settings, and cache/table behavior.
- `full_history_ts_low_` and `flush_skip_reschedule_` affect whether flushes are postponed to retain in-memory user-defined timestamp history; `SuperVersion::Init` snapshots the low watermark for readers.
- `seqno_to_time_mapping` is published through `SuperVersion` and shared with later superversions or flush jobs, with debug assertions that it exists when time preservation is enabled.
- `next_epoch_number_` and `RecoverEpochNumbers` track the per-CF epoch numbering state used by file metadata.
- `running_ts_sz_` and `ts_sz_for_record_` in `ColumnFamilySet` track live CF timestamp sizes and the subset that must be recorded.
- `data_dirs_` caches opened `FSDirectory` handles for CF paths, while path registration/unregistration informs the environment about DB data directories.

The file does not directly serialize MANIFEST records, WAL records, table files, blob files, or OPTIONS files. Those durable actions occur in surrounding components. This code supplies the in-memory metadata and invariants those components use to decide what must be flushed, compacted, retained, recovered, or deleted.

## Dependencies

Major dependencies include:

- `db/column_family.h` for declarations and member layout.
- `db/db_impl/db_impl.h` for mutex, directory creation, obsolete file discovery, and purge integration.
- `db/version_set.h` and `VersionStorageInfo` for current version state, file sizes, pending compaction debt, epoch recovery, and live-version accounting.
- `db/memtable_list.h`, `MemTable`, and range tombstone iterators for mutable/immutable write buffers.
- `db/compaction/compaction_picker_*` for level, universal, FIFO, null, automatic, and manual compaction selection.
- `db/write_controller.h` for stop, delay, and compaction-pressure tokens.
- `db/internal_stats.h` and monitoring utilities for CF counters and runtime statistics.
- `db/blob/blob_file_cache.h`, `db/blob/blob_source.h`, and `db/blob/blob_file_partition_manager.h` for blob-read and direct-write integration.
- `options/options_helper.h`, `options/cf_options.h`, `rocksdb/convenience.h`, and `rocksdb/table.h` for option parsing, validation, and table-factory introspection.
- `util/compression.h`, `file/sst_file_manager_impl.h`, `DeleteScheduler`, `CacheReservationManager`, `ThreadLocalPtr`, `autovector`, and filesystem abstractions.

## Integration Points

`DBImpl` uses this file's objects for column-family handles, queues, superversion installation, obsolete-file cleanup, directory creation, write-stall notifications, and read/write access to current LSM state.

`VersionSet` and manifest application create/drop CFs through `ColumnFamilySet`, install `Version` objects into `ColumnFamilyData`, and rely on CFD refcounts to keep versions and files alive while old superversions are referenced.

The write path uses `ColumnFamilyMemTablesImpl` to map column-family IDs in `WriteBatch` records to `MemTable*`, log numbers, and internal handles. Memtable creation and max-write-buffer behavior here directly affect flush scheduling and write stalls.

Read paths and iterators depend on `SuperVersion` pinning mutable memtable, immutable memtable-list version, and current `Version` so files and memtables cannot disappear while a read operates.

Compaction and flush jobs share `SuperVersion` or current CFD state for snapshots, timestamp history, memtable retention, `SeqnoToTimeMapping`, blob source/cache access, and cache-reservation accounting.

Listeners configured in immutable options are called when handles start deletion, making this file part of the public lifecycle notification path.

## Risks

- Reference-count correctness is critical. `ColumnFamilyData`, `SuperVersion`, `Version`, mutable memtable, and immutable memtable-list references are interdependent; missing a ref/unref can cause leaks, premature deletion, or old reads seeing freed memory.
- Thread-local superversion caching is subtle. `kSVInUse`, `kSVObsolete`, `Swap`, `Scrape`, and compare-and-swap must preserve the invariant that TLS never owns the last SV reference and that full cleanup only happens where the DB mutex can be held.
- Many methods require the DB mutex, single-threaded write-thread context, or both. Violating those requirements around `ColumnFamilySet` maps, `SetDropped`, `CreateColumnFamily`, `RemoveColumnFamily`, `InstallSuperVersion`, and `UnrefAndTryDelete` risks registry corruption or races with column-family drop.
- Option sanitization silently adjusts user settings such as L0 thresholds, min write buffers, TTL/periodic compaction defaults, dynamic level bytes, and blob direct-write flags. Behavioral regressions here can change performance, retention, or data-loss protections across DB open.
- Write-stall control is feedback-based. Changes to thresholds or rate adjustment ratios can over-throttle writes, fail to avoid hard stops, or create cross-CF interference through shared `WriteController` tokens.
- `ColumnFamilyHandleImpl::~ColumnFamilyHandleImpl` holds a copy of initial CF options to keep shared option-owned resources alive during cleanup. Removing that pattern could create lifetime bugs with listeners, compaction filters, or factories.
- `SetDropped` removes registry visibility before old handles/readers are gone. Code that assumes a dropped CF is destroyed immediately can leak files, schedule invalid work, or reject valid reads from old handles.
- User-defined timestamp behavior is guarded by comparator timestamp size and `persist_user_defined_timestamps`. The flush-postponement path can preserve in-memory history but can also delay flush progress if timestamp low-watermark semantics are changed incorrectly.
- Blob direct-write validation rejects several write modes. Relaxing those checks without matching write-path guarantees could break ordering or recovery assumptions.

## Test Signals

Useful test signals include:

- Column-family create/drop tests where handles outlive `DropColumnFamily`, reads through old handles still work, writes fail or are ignored according to options, and obsolete files are purged only after final handle release.
- Superversion tests that install new versions/memtables, exercise thread-local cached reads, reset TLS state, and verify old versions/memtables are deleted only after all references drain.
- Dynamic option tests for `SetOptions`, including mutable-only enforcement, validation failures, refresh of derived options, and write buffer size updates on install.
- DB open/recovery tests for `SanitizeCfOptions`, CF path registration/cleanup, TTL/periodic compaction defaults, atomic flush with min-write-buffer merge, and multi-path compaction-style compatibility.
- Write-stall tests covering memtable limit, L0 file-count limit, pending compaction bytes, delay-to-normal recovery, disabled auto-compactions, and compaction-pressure token creation.
- Compaction picker tests for level/universal/FIFO/null styles, manual `CompactRange`, range-overlap conflict detection, and `FinalizeInputInfo` against the current version.
- User-defined timestamp tests for `SetFullHistoryTsLow`, `SetFlushSkipReschedule`, `ShouldPostponeFlushToRetainUDT`, non-persisted timestamp compatibility checks, and superversion low-watermark snapshots.
- Blob feature tests for blob compression validation, blob garbage-collection thresholds, blob direct-write incompatibilities, and `SetBlobPartitionManager` lifetime.
- WAL retention tests in two-phase commit mode verifying `OldestLogToKeep` accounts for prepared sections in mutable and immutable memtables.
- Stress/ASAN/TSAN tests that create/drop CFs while readers, iterators, flushes, and compactions keep old superversions alive.
