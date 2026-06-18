# sources/storage-engines/rocksdb/db/column_family.h

## Purpose

`column_family.h` declares the internal column-family object model for RocksDB. It defines the handle implementation exposed through the public DB API, the `SuperVersion` snapshot type used by reads and background jobs, the `ColumnFamilyData` metadata object for each live or dropped column family, the `ColumnFamilySet` registry owned by `DBImpl`, and helper wrappers used by iteration and write-batch application.

The header is mostly an ownership and concurrency contract. It explains how `DBImpl`, `ColumnFamilyHandle`, `ColumnFamilyData`, `MemTable`, `MemTableListVersion`, `Version`, and `SuperVersion` reference each other so a point-in-time LSM view remains valid while column families are changed, flushed, compacted, or dropped.

## Important APIs, Types, and Functions

Top-level validation and option helpers:

- `CheckCompressionSupported`, `CheckConcurrentWritesSupported`, and `CheckCFPathsSupported` validate individual compatibility groups before DB open or dynamic option updates.
- `SanitizeCfOptions` normalizes `ColumnFamilyOptions` using immutable DB options and read-only state.
- `GetInternalTblPropCollFactory` wraps user table-properties collector factories in internal collector factories.
- `kIncSlowdownRatio` is exported for write-stall delay adjustment logic.

`ColumnFamilyHandleImpl`:

- Implements `ColumnFamilyHandle` and owns a reference to `ColumnFamilyData`.
- Exposes `cfd()`, `db()`, `GetID`, `GetName`, `GetDescriptor`, and `GetComparator`.
- Stores `DBImpl*` and `InstrumentedMutex*` so descriptor access and destruction can synchronize with DB state.

`ColumnFamilyHandleInternal`:

- A dummy handle used by internal write-batch/memtable paths when code expects a `ColumnFamilyHandle`.
- Overrides `cfd()` to return `internal_cfd_` and does not ref-count the CFD.

`SuperVersion`:

- Holds a `ColumnFamilyData*`, mutable `ReadOnlyMemTable*`, immutable `MemTableListVersion*`, current `Version*`, current `MutableCFOptions`, version number, write-stall condition, `full_history_ts_low`, and shared `SeqnoToTimeMapping`.
- Provides `Ref`, `Unref`, `Cleanup`, and `Init` for reference management.
- Exposes `ShareSeqnoToTimeMapping` and `GetSeqnoToTimeMapping` for read/flush users.
- Defines TLS sentinels `kSVInUse` and `kSVObsolete` for `ColumnFamilyData`'s thread-local superversion cache.

`ColumnFamilyData`:

- Represents one column family and owns its immutable/mutable options, comparator, table/blob caches, internal stats, memtable, immutable memtable list, current version pointer, current superversion pointer, compaction picker, path directories, write-stall token, timestamp history state, and queue flags.
- Public identity and lifetime APIs: `GetID`, `GetName`, `Ref`, `UnrefAndTryDelete`, `SetDropped`, `IsDropped`, `set_initialized`, and `initialized`.
- Option APIs: `soptions`, `ioptions`, `GetCurrentMutableCFOptions`, `GetLatestMutableCFOptions`, `GetLatestCFOptions`, static `ValidateOptions`, and `SetOptions`.
- LSM state APIs: `imm`, `mem`, `IsEmpty`, `dummy_versions`, `current`, `SetCurrent`, live/SST/blob size accessors, `OldestLogToKeep`, `ConstructNewMemtable`, `CreateNewMemtable`, and `SetMemtable`.
- Cache/blob APIs: `table_cache`, `blob_file_cache`, `blob_source`, `blob_partition_manager`, `blob_partition_manager_handle`, and `SetBlobPartitionManager`.
- Compaction APIs: `NeedsCompaction`, `PickCompaction`, `RangeOverlapWithCompaction`, `RangesOverlapWithMemtables`, `CompactRange`, `compaction_picker`, `kCompactAllLevels`, and `kCompactToBaseLevel`.
- Comparator and table-properties APIs: `user_comparator`, `internal_comparator`, and `internal_tbl_prop_coll_factories`.
- Superversion APIs: `GetSuperVersion`, `GetReferencedSuperVersion`, `GetThreadLocalSuperVersion`, `ReturnThreadLocalSuperVersion`, `GetSuperVersionNumber`, `InstallSuperVersion`, and `ResetThreadLocalSuperVersions`.
- Queue and write-stall APIs: `set_queued_for_flush`, `set_queued_for_compaction`, `queued_for_flush`, `queued_for_compaction`, `GetWriteStallConditionAndCause`, and `RecalculateWriteStallConditions`.
- Directory and timestamp APIs: `AddDirectories`, `GetDataDir`, `SetFullHistoryTsLow`, `GetFullHistoryTsLow`, `ShouldPostponeFlushToRetainUDT`, `SetFlushSkipReschedule`, and `GetAndClearFlushSkipReschedule`.
- Miscellaneous state APIs: `write_buffer_mgr`, `GetFileMetadataCacheReservationManager`, `SetMempurgeUsed`, `GetMempurgeUsed`, `NewEpochNumber`, `GetNextEpochNumber`, `SetNextEpochNumber`, `ResetNextEpochNumber`, `RecoverEpochNumbers`, `GetUnflushedMemTableCountForWriteStallCheck`, `AllowIngestBehind`, and `GetIngestSstLock`.

`ColumnFamilySet`:

- Owns all running `ColumnFamilyData` instances in maps keyed by name and ID, plus a circular linked list for iteration.
- Provides `GetDefault`, `GetColumnFamily` by ID/name, ID allocation/update helpers, `NumberOfColumnFamilies`, `CreateColumnFamily`, timestamp-size maps, iterators, access to shared table cache/write buffer manager/write controller, and fast-SST-open flags.
- Declares strict thread-safety rules: creation/removal require DB mutex plus single-threaded write thread; iteration requires DB mutex unless wrapped by `RefedColumnFamilySet`; lookup is allowed under DB mutex or write thread.

`RefedColumnFamilySet`:

- Wraps `ColumnFamilySet` iteration so each visited CFD is refed while visible to caller code that may release the DB mutex inside the loop body.

`ColumnFamilyMemTablesImpl`:

- Implements `ColumnFamilyMemTables` for write-batch application.
- `Seek` selects a CFD by ID, `GetLogNumber` returns the selected CF's log number, `GetMemTable` returns the current mutable memtable, `GetColumnFamilyHandle` returns an internal handle, and `current` exposes the selected CFD.

Free helper functions:

- `GetColumnFamilyID` maps a nullable handle to a CF ID, returning default ID 0 for null.
- `GetColumnFamilyUserComparator` returns a handle's user comparator if present.
- `GetImmutableOptions` returns immutable options from an internal handle.

## Control Flow

The declared lifecycle starts when `ColumnFamilySet::CreateColumnFamily` constructs a `ColumnFamilyData` and inserts it into the set. DB recovery or MANIFEST application then connects it to versions, memtables, and superversions. Public users hold `ColumnFamilyHandleImpl`, which increments the CFD refcount and can outlive a dropped CF.

At read time, callers acquire a `SuperVersion` from `ColumnFamilyData`. The superversion refs the mutable memtable, immutable memtable-list version, and current version, which pins the exact LSM view for iterators, gets, compactions, and flushes. The thread-local superversion API lets repeated reads avoid the DB mutex until `InstallSuperVersion` marks cached entries obsolete.

At write time, `ColumnFamilyMemTablesImpl` maps write-batch CF IDs to the current mutable memtable and log number. If a memtable rotates, `CreateNewMemtable` and `InstallSuperVersion` publish the new mutable memtable while older superversions preserve the old view.

When a CF is dropped, `SetDropped` removes it from the running registry but does not destroy the data immediately. Existing handles, superversions, reads, and compactions can keep refs. `UnrefAndTryDelete` eventually destroys the object once only self/superversion references remain and cleanup can safely unref all pinned objects.

Compaction control flows through `NeedsCompaction`, `PickCompaction`, and `CompactRange`, but the actual algorithms live in the compaction picker classes. The header exposes enough state for `DBImpl` and background jobs to schedule work while honoring mutex requirements.

## State and Persistence Behavior

The header defines the primary in-memory state that reflects durable RocksDB metadata:

- `id_`, `name_`, `log_number_`, and `max_column_family_` connect running CF objects to MANIFEST/WAL metadata.
- `dummy_versions_`, `current_`, `Version`, and `VersionStorageInfo` model durable SST/blob file state for a CF.
- `mem_` and `imm_` model unflushed data that may be WAL-protected and later flushed.
- `SuperVersion` snapshots combine memtable, immutable memtable list, current version, mutable options, timestamp history low watermark, and sequence-number-to-time mapping for point-in-time reads.
- `initial_cf_options_`, `ioptions_`, and `mutable_cf_options_` split persisted/configured options into immutable and dynamically changeable runtime forms.
- `data_dirs_` and CF paths connect a column family to filesystem directories.
- `full_history_ts_low_`, `flush_skip_reschedule_`, and timestamp-size maps express user-defined timestamp retention state.
- `next_epoch_number_` tracks per-CF epoch assignment for file metadata.

The declarations do not directly persist this state. They define the interfaces used by `VersionSet`, DB open/recovery, flush, compaction, and options code to translate persisted metadata into live state and back.

## Dependencies

The header depends on core RocksDB internals and public APIs:

- Memtable and versioning: `db/memtable_list.h`, `Version`, `VersionSet`, `VersionStorageInfo`, and `db/write_batch_internal.h`.
- Options and public API types: `options/cf_options.h`, `rocksdb/db.h`, `rocksdb/env.h`, and `rocksdb/options.h`.
- Caches and collectors: `db/table_cache.h`, `cache/cache_reservation_manager.h`, and `db/table_properties_collector.h`.
- Write and compaction coordination: `db/write_controller.h`, `rocksdb/compaction_job_stats.h`, `SnapshotChecker`, `CompactionPicker`, and `Compaction`.
- Observability/tracing: `trace_replay/block_cache_tracer.h`, `IOTracer`, and internal stats declarations.
- Infrastructure: `util/thread_local.h`, `util/hash_containers.h`, `util/cast_util.h`, `port::RWMutex`, atomics, strings, vectors, and unordered maps.

Forward declarations reduce include weight for heavy classes such as `DBImpl`, `BlobFileCache`, `BlobFilePartitionManager`, `BlobSource`, and `InternalStats`.

## Integration Points

`DBImpl` owns a `ColumnFamilySet`, creates user handles, uses `ColumnFamilyData` for read/write/flush/compaction queues, and calls `InstallSuperVersion` when memtables or versions change.

`VersionSet` and MANIFEST application create/drop CFs, maintain `Version` chains under each CFD's dummy version list, and use CF IDs to tie durable file edits to runtime objects.

The write batch path uses `ColumnFamilyMemTablesImpl` to find the right memtable for each record by column-family ID. A null external handle maps to default CF ID 0 through `GetColumnFamilyID`.

Read paths, iterators, compactions, and flush jobs use `SuperVersion` to keep old memtables and SST metadata alive while concurrent state changes publish newer views.

Compaction pickers, blob file components, table caches, cache reservation managers, write buffer manager, write controller, and table property collectors are all owned or accessed through `ColumnFamilyData`.

User-defined timestamp support integrates through comparator timestamp size, `full_history_ts_low`, timestamp-size maps in `ColumnFamilySet`, and flush postponement APIs.

External file ingestion and range tombstone conversion coordinate through the per-CF `ingest_sst_lock_`.

## Risks

- The header's mutex/write-thread requirements are part of the correctness contract. Callers that mutate `ColumnFamilySet` maps or CFD queue/drop state outside those contexts can race with drop, recovery, or write-batch lookup.
- `ColumnFamilyHandleInternal` intentionally does not ref-count. It is safe only when the caller already guarantees the selected CFD lifetime through DB mutex or write-thread serialization.
- `SuperVersion` stores raw pointers and uses manual reference counting. Any new field with ownership semantics must participate in `Init`, `Cleanup`, installation, and TLS invalidation.
- `ColumnFamilyData` has many raw pointers whose lifetimes are externally constrained: current version, memtable, `ColumnFamilySet`, `WriteBufferManager`, DB options, table cache, and write controller. Ownership must remain clear when adding APIs.
- Dropped column families remain readable while handles exist, so registry absence is not equivalent to object destruction.
- `GetCurrentMutableCFOptions` and `GetLatestMutableCFOptions` intentionally differ. Code that uses the latest options before a superversion install can observe settings not yet published to readers.
- `SetFullHistoryTsLow` ignores persisted UDT low-watermarks if the comparator no longer has timestamps. This protects reopen-after-disable cases but makes timestamp support sensitive to comparator behavior.
- `RefedColumnFamilySet` unrefs on iterator increment/destruction. Misusing copied iterators or holding returned raw pointers beyond the protected scope can invalidate the safety it provides.
- The circular linked list relies on destructor unlinking and dummy sentinel invariants; partial construction/destruction bugs can break iteration across all CFs.

## Test Signals

High-value tests exercising this header's contracts include:

- Compile-time and unit coverage for public handle methods, descriptor retrieval under mutex, null/default handle ID mapping, and internal handle behavior.
- Column-family set tests for create, lookup by name/ID, default cache, max-ID tracking, timestamp-size maps, iteration, and removal on drop/destruction.
- Refcount/lifetime tests where old handles, iterators, superversions, flushes, and compactions keep a dropped CF alive until the final unref.
- Read-path tests proving `SuperVersion` pins old memtables/versions while new superversions are installed and thread-local caches are invalidated.
- Dynamic option tests distinguishing latest mutable options from the mutable options captured in the current superversion.
- Write-batch tests that route records to the proper memtable through `ColumnFamilyMemTablesImpl`, including missing CF behavior.
- User-defined timestamp tests for timestamp-size maps, `full_history_ts_low` monotonicity, flush postponement, and disabled-UDT reopen behavior.
- External file ingestion/range tombstone conversion tests that exercise the per-CF RW lock.
- TSAN/stress coverage around DB mutex release during `RefedColumnFamilySet` iteration and concurrent drop/flush/compaction scheduling.
