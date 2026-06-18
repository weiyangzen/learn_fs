# sources/storage-engines/rocksdb/db/db_impl/db_impl.h

## Purpose

`db_impl.h` declares `DBImpl`, the central concrete implementation of the public RocksDB `DB` interface. It is the engine entry point used directly by core RocksDB and wrapped by higher-level implementations such as transactional, blob, secondary, follower, and compacted DB variants. The header is intentionally broad: it exposes public `DB` overrides, internal hooks for transactions and column families, background flush/compaction orchestration, WAL and recovery plumbing, snapshot management, stats/tracing APIs, external file ingestion, direct blob-write support, and a large amount of synchronized persistent state.

The file also defines small supporting types:

- `Directories`, which owns DB, WAL, and data-path `FSDirectory` handles and centralizes directory close behavior.
- `DBOpenLogRecordReadReporter`, a WAL reader corruption/old-record reporter used during open/recovery.
- `GetWithTimestampReadCallback`, which restricts visibility to a maximum sequence for timestamped reads.
- Free helper APIs for option sanitization, flush compression selection, WAL-retention decisions after memtable flushes, and option range clipping.

## Important APIs, Types, and Functions

### Public DB interface implementation

`DBImpl` overrides nearly the full public `rocksdb::DB` surface:

- Write APIs: `Put`, timestamped `Put`, `PutEntity`, attribute-group `PutEntity`, `Merge`, timestamped `Merge`, `Delete`, timestamped `Delete`, `SingleDelete`, timestamped `SingleDelete`, `DeleteRange`, `Write`, `WriteWithCallback`, and `IngestWriteBatchWithIndex`.
- Read APIs: `Get`, `GetEntity`, `GetMergeOperands`, `MultiGet`, `MultiGetEntity`, `KeyMayExist`, iterator creation, multi-CF/coalescing iterators, `NewMultiScan`, and snapshot APIs.
- Column-family APIs: `CreateColumnFamily`, `CreateColumnFamilies`, `DropColumnFamily`, `DropColumnFamilies`, import-based CF creation, and `DefaultColumnFamily`.
- Maintenance APIs: `Flush`, `FlushWAL`, `SyncWAL`, `LockWAL`, `UnlockWAL`, `CompactRange`, `CompactFiles`, `PauseBackgroundWork`, `ContinueBackgroundWork`, auto/manual compaction control, `WaitForCompact`, `PromoteL0`, checksum verification, live-file metadata, WAL listing, update iteration, tracing, block-cache tracing, IO tracing, stats history, and dynamic option updates.

These public overrides delegate into narrower internal entry points such as `GetImpl`, `WriteImpl`, `PipelinedWriteImpl`, `WriteImplWALOnly`, `RunManualCompaction`, `FlushMemTable`, `AtomicFlushMemTables`, `Recover`, `CloseImpl`, and background work helpers.

### Read-side internals

`GetImplOptions` is the main read dispatch structure. It carries the target column family, plain value output, wide-column output, timestamp output, merge operand output, read callback, blob-index marker, and a `get_value` switch for `GetMergeOperands`.

Important read helpers include:

- `GetImpl`, the common point lookup path used by `Get`, `KeyMayExist`, and `GetMergeOperands`.
- `NewIteratorImpl` and `NewInternalIterator`, which build public and internal iterator trees over memtables and SST versions.
- `MultiGetCommon`, `MultiCFSnapshot`, `PrepareMultiGetKeys`, `MultiGetImpl`, and `MultiGetWithCallbackImpl`, which coordinate batched lookups, sorted key contexts, per-CF `SuperVersion` references, and a consistent multi-CF snapshot.
- `GetLatestSequenceForKey`, which searches memtables and optionally files for the latest visible record for conflict checking or metadata purposes.
- Timestamp guards `FailIfCfHasTs`, `FailIfTsMismatchCf`, `FailIfReadCollapsedHistory`, and `IncreaseFullHistoryTsLowImpl`.
- Blob read postprocessing helpers `ResolveDirectWritePlainValue`, `ResolveDirectWriteWideColumns`, `MaybeResolveDirectWriteValue`, `MaybeResolveMemtableBlobValue`, and `PostprocessMemtableValueRead`.

### Write-side internals

`WriteImpl` is the main write pipeline. It supports callbacks before WAL write, pre-release callbacks after WAL write and before memtable application, post-memtable callbacks before sequence publication, write-batch-with-index ingestion, memtable-disabling transaction records, WAL/log reference plumbing, and blob direct-write materialization.

Important write structures and helpers:

- `WriteContext` bundles `SuperVersionContext` plus memtables to free after a write.
- `WalContext` tracks whether WAL and WAL directory sync are needed, the active writer, WAL size bookkeeping, and previous WAL size.
- `AssignOrder` and `PublishLastSeq` parameterize WAL-only writes and two-queue transaction behavior.
- `DeferredPutEntityBatch` stages logical wide-column `PutEntity` operations so `WriteImpl` can serialize them after it knows the selected memtable/blob generation.
- `MaybeTransformBatchForBlobDirectWrite`, `AppendPreprocessedPutEntityToBatch`, `AppendSortedPutEntityToBatch`, `PutEntityFastPath`, `WritePreprocessedPutEntityBatch`, and `SyncBlobDirectWriteManagers` implement the blob direct-write fast path.
- `PreprocessWrite`, `MergeBatch`, `WriteToWAL`, `WriteGroupToWAL`, `ConcurrentWriteGroupToWAL`, `UnorderedWriteMemtable`, `ScheduleFlushes`, `SwitchMemtable`, `SwitchWAL`, `HandleWriteBufferManagerFlush`, `DelayWrite`, `ThrottleLowPriWritesIfNeeded`, and `WriteBufferManagerStallWrites` shape the write hot path.

`write_thread_` is the primary write queue; `nonmem_write_thread_` is used for writes that only touch WAL, such as two-phase commit prepares. Configuration booleans such as `two_write_queues_`, `manual_wal_flush_`, `last_seq_same_as_publish_seq_`, `seq_per_batch_`, and `batch_per_txn_` alter ordering, publication, and recovery semantics.

### Recovery and WAL processing

Recovery is split into descriptor, file-number, WAL, and memtable flush phases:

- `Recover`, `NewDB`, `Open`, `SetupDBId`, `SetDBId`, `MaybeUpdateNextFileNumber`, `TrackExistingDataFiles`, `UntrackDataFiles`, `LogAndApplyForRecovery`, `SetupLogFilesRecovery`, and `RecoverLogFiles` rebuild DB state from MANIFEST and WALs.
- `ProcessLogFiles`, `ProcessLogFile`, `InitializeLogReader`, `ProcessLogRecord`, `InitializeWriteBatchForLogRecord`, `InvokeWalFilterIfNeededOnWalRecord`, `InsertLogRecordToMemtable`, `MaybeWriteLevel0TableForRecovery`, `WriteLevel0TableForRecovery`, and `MaybeFlushFinalMemtableOrRestoreActiveLogFiles` implement WAL replay.
- `DBOpenLogRecordReadReporter` records corruption, old log records, and the corrupted WAL number.
- `HandleNonOkStatusOrOldLogRecord`, `MaybeReviseStopReplayForCorruption`, `MaybeHandleStopReplayForCorruptionForInconsistency`, `UpdatePredecessorWALInfo`, and `CheckSeqnoNotSetBackDuringRecovery` protect replay ordering and corruption policies.
- `RecoveredTransaction` stores recovered 2PC transaction batches keyed by first sequence number, tracks whether they are unprepared, and marks WALs containing prepare sections through `LogsWithPrepTracker`.

WAL state is kept in `cur_wal_number_`, `wal_recycle_files_`, `min_wal_number_to_recycle_`, `wal_dir_synced_`, `wal_empty_`, `alive_wal_files_`, `logs_`, `wals_total_size_`, `cached_recoverable_state_`, and queues for log writers needing close/free. WAL persistence helpers include `SyncWalImpl`, `SyncClosedWals`, `MarkLogsSynced`, `MarkLogsNotSynced`, `ApplyWALToManifest`, `GetLogSizeAndMaybeTruncate`, `RestoreAliveLogFiles`, `CreateWALWriter`, `StartWALFile`, `CreateWAL`, and async WAL precreation helpers.

### Background flush, compaction, purge, and periodic work

The class owns several explicit work queues and state machines:

- `FlushRequest`, `BGFlushArg`, and `FlushThreadArg` represent pending flushes.
- `ManualCompactionState`, `PrepickedCompaction`, and `CompactionArg` represent manual/pre-picked/background compactions.
- `PurgeFileInfo` records obsolete files scheduled for purge.
- `AsyncFileOpenState` and `AsyncWALPrecreateState` track asynchronous table opening and WAL precreation.

Scheduling and execution use:

- `MaybeScheduleFlushOrCompaction`, `EnqueuePendingFlush`, `EnqueuePendingCompaction`, `SchedulePendingPurge`, `BGWorkCompaction`, `BGWorkBottomCompaction`, `BGWorkFlush`, `BGWorkPurge`, `BackgroundCallCompaction`, `BackgroundCallFlush`, `BackgroundCallPurge`, `BackgroundCompaction`, and `BackgroundFlush`.
- Flush implementation helpers `FlushMemTableToOutputFile`, `FlushMemTablesToOutputFiles`, `AtomicFlushMemTablesToOutputFiles`, `SelectColumnFamiliesForAtomicFlush`, `AssignAtomicFlushSeq`, `GenerateFlushRequest`, `WaitForFlushMemTable`, and `WaitForFlushMemTables`.
- Compaction helpers `CompactFilesImpl`, `PrepareTrivialMoveEdit`, `CommitTrivialMove`, `FindMinimumEmptyLevelFitting`, `ReFitLevel`, `PickCompactionFromQueue`, `ShouldPickCompaction`, `EnoughRoomForCompaction`, `RequestCompactionToken`, `ShouldRescheduleFlushRequestToRetainUDT`, and manual compaction queue helpers.
- Periodic task helpers `StartPeriodicTaskScheduler`, `CancelPeriodicTaskScheduler`, `RegisterRecordSeqnoTimeWorker`, `PrintStatistics`, `DumpStats`, `PersistStats`, `FlushInfoLog`, `RecordSeqnoToTimeMapping`, and `TriggerPeriodicCompaction`.

Background state counters include unscheduled/scheduled/running flushes, compactions, bottom-priority compactions, purge jobs, background pressure callbacks, paused background work/compaction counters, and condition variables for waiters.

### File lifecycle and persistence helpers

File lifecycle safety is a major theme:

- `FindObsoleteFiles`, `PurgeObsoleteFiles`, `SchedulePurge`, `DeleteObsoleteFiles`, `DeleteObsoleteFileImpl`, `ShouldKeepBlobFileDuringPurge`, `ShouldPurge`, `MarkAsGrabbedForPurge`, `DisableFileDeletions`, and `EnableFileDeletions` control deletion.
- `pending_outputs_` protects files with numbers at or above captured boundaries while background jobs create outputs.
- `min_options_file_numbers_`, `CaptureOptionsFileNumber`, and `ReleaseOptionsFileNumber` protect OPTIONS files, especially for remote compaction.
- `ReserveFileNumbersBeforeIngestion`, `RollbackPreparedFileIngestion`, `PrepareFileIngestion`, and `CommitFileIngestionHandles` coordinate file-number reservations for external SST ingestion.
- `Directories` returns DB/WAL/data directories and closes all opened directories, treating `NotSupported` close statuses as non-fatal.

Free helpers `GetDBRecoveryEditForObsoletingMemTables`, `PrecomputeMinLogNumberToKeep2PC`, `PrecomputeMinLogNumberToKeepNon2PC`, and `FindMinPrepLogReferencedByMemTable` determine WAL retention after flushes in 2PC, atomic flush, and non-2PC modes.

## Control Flow

### Open and recovery

`Open` constructs `DBImpl`, validates/sanitizes options, locks the DB, initializes directories and identities, loads MANIFEST state into `VersionSet`, discovers existing SST/blob files, advances next file numbers, processes WAL filters, replays sorted WALs through `RecoverLogFiles`, flushes or restores replayed memtables/WAL state as needed, installs column-family `SuperVersion`s, initializes persistent stats, starts periodic/async tasks, and marks the DB opened. Recovery accumulates version edits in `RecoveryContext` and persists them through `LogAndApplyForRecovery` after a new MANIFEST is ready.

### Foreground write path

User writes enter `Write`/`Put`/`Merge`/`Delete` wrappers and converge on `WriteImpl` or the `PutEntity` fast path. The write joins the appropriate `WriteThread`, optionally merges with a group, runs pre-WAL callbacks and validation, may rotate WAL/memtable through `PreprocessWrite`, writes to WAL, syncs WAL/directory when requested, applies to memtable unless disabled, runs callbacks, publishes sequence numbers, handles blob direct-write manager sync/rollback concerns, schedules flush/compaction, and updates background error state on I/O or memtable insertion failures.

### Read path

Reads resolve column-family handles to `ColumnFamilyData`, obtain a `SuperVersion`, choose explicit or implicit sequence snapshots, validate timestamp constraints, search mutable/immutable memtables, files, merge operands, range tombstones, and blob-backed values, then postprocess values or columns. Multi-key and multi-CF reads use `MultiCFSnapshot` to obtain a consistent view across all column families, then group sorted key contexts per CF for batched lookup.

### Flush and compaction

Writes or explicit API calls enqueue flush requests when memtables become immutable or when WAL/memory pressure requires it. Background flush workers persist memtables to L0 files, write version edits, install new `SuperVersion`s, update WAL retention, and schedule purges/compactions. Compaction workers pick eligible column families, optionally use pre-picked/manual state, write new output files or prepare/commit trivial moves, install version edits, release compaction files, notify listeners, and purge obsolete inputs.

### Shutdown

`Close`, `CloseImpl`, `CloseHelper`, `CancelAllBackgroundWork`, `WaitForBackgroundWork`, `MaybeWriteWalMarkersToManifestOnClose`, `MaybeReleaseTimestampedSnapshotsAndCheck`, `NotifyOnDBShutdownBegin`, and directory/log close helpers coordinate a controlled shutdown. State fields distinguish shutdown notification, shutdown initiation, atomic shutting down, closed status, and saved close status for repeat calls.

## State and Persistence Behavior

Persistent DB identity is held in `db_id_`; per-open identity is `db_session_id_`. `versions_` owns MANIFEST/version metadata and sequence-number state. WAL durability is tracked with `logs_`, `alive_wal_files_`, `cur_wal_number_`, `wal_dir_synced_`, `wal_empty_`, `wals_total_size_`, and `LogWriterNumber` sync markers. WAL sync metadata can be committed to MANIFEST with `ApplyWALToManifest` and closed-WAL syncing.

The class uses several locks with documented ownership:

- `mutex_` protects most DB and column-family state and is cache-aligned because it is hot.
- `options_mutex_` protects option consistency and is acquired before `mutex_`.
- `wal_write_mutex_` protects WAL writers, current WAL number, and some WAL lists, especially with two write queues.
- `stats_history_mutex_` protects in-memory stats history.
- `closing_mutex_`, `bg_cv_`, `wal_sync_cv_`, `atomic_flush_install_cv_`, and `switch_cv_` coordinate close, background work, WAL sync, atomic flush installation, and unordered/pipelined memtable writers.

Persistence-related state includes:

- Memtable/WAL linkage through `ColumnFamilyMemTablesImpl`, `flush_scheduler_`, `trim_history_scheduler_`, `pending_outputs_`, and WAL retention helpers.
- File deletion safety through `disable_delete_obsolete_files_`, `pending_purge_obsolete_files_`, `purge_files_`, `files_grabbed_for_purge_`, `pending_outputs_`, and `min_options_file_numbers_`.
- Snapshot visibility through `snapshots_`, `timestamped_snapshots_`, `snapshot_checker_`, `track_published_seq_in_snapshot_context_`, and `last_seq_same_as_publish_seq_`.
- Persistent stats through `persistent_stats_cfd_exists_`, `persist_stats_cf_handle_`, `stats_history_`, `stats_slice_`, format-version processing, and periodic stats tasks.
- Blob direct write through `blob_direct_write_cf_count_`, BDW per-CF initialization/registration, in-flight blob file preservation, and read-side blob-index resolution before files are visible through MANIFEST.

## Dependencies and Integration Points

This header integrates with most of RocksDB core:

- Column family and versioning: `ColumnFamilyData`, `ColumnFamilyHandleImpl`, `ColumnFamilyMemTablesImpl`, `Version`, `VersionSet`, `VersionEdit`, `SuperVersion`, and MANIFEST log-and-apply.
- Write and recovery: `WriteBatch`, `WriteBatchWithIndex`, `WriteThread`, `WriteCallback`, `UserWriteCallback`, `PreReleaseCallback`, `PostMemTableCallback`, `LogsWithPrepTracker`, WAL reader/writer, and WAL filters.
- Storage and filesystems: `Env`, `FileSystem`, `FSDirectory`, `FileOptions`, `WalManager`, table cache, SstFileManager behavior, external SST ingestion, import jobs, and checksum verification.
- LSM maintenance: `FlushJob`, `FlushScheduler`, `Compaction`, `CompactionJob`, `CompactionIterator`, compaction task limiter tokens, range deletion aggregation, and trim-history scheduling.
- Read stack: memtables, internal iterators, merging iterators, `ReadCallback`, `SnapshotChecker`, `MultiGetContext`, `BlobFetcher`, and timestamp comparators.
- Observability and control: `InternalStats`, `EventLogger`, info log flushing, `PeriodicTaskScheduler`, tracing, block-cache tracing, IO tracing, thread status hooks, and background job pressure notification.
- Higher layers: transaction classes and wrappers are friends or direct callers of internal APIs such as `WriteImpl`, recovered transaction maps, and `GetImpl`.

## Risks and Maintenance Concerns

- Synchronization is complex. WAL state has different locking rules depending on whether two write queues are enabled; some fields can be read by write-thread affinity while others require `mutex_`, `wal_write_mutex_`, or both. Any change to WAL rotation, sync, or deletion must preserve the documented lock ordering: acquire `mutex_` before `wal_write_mutex_` when both are needed.
- Sequence publication is subtle. `LastSequence`, `LastPublishedSequence`, `LastAllocatedSequence`, `seq_per_batch_`, transaction modes, and `last_seq_same_as_publish_seq_` affect visibility, recovery, and write conflict checks.
- File deletion safety relies on approximate lower bounds such as `pending_outputs_`, pending options file numbers, prep-log references, WAL sync state, and BDW in-flight file checks. Incorrect retention math can delete files before MANIFEST installation or keep obsolete files indefinitely.
- Recovery has many policy branches: read-only open, retry open, WAL filter decisions, old log records, corrupted WAL handling, `avoid_flush_during_recovery`, 2PC/unprepared transactions, and sequence rollback checks.
- Blob direct-write is intertwined with write and read paths. Writes may defer serialization until `PreprocessWrite`, and reads may need to resolve blob indices before blob files are visible through normal version metadata.
- Background scheduling counters and queues are tightly coupled. Failing to update scheduled/running/unscheduled counters, condition variables, or ref-counted `ColumnFamilyData` queue membership can deadlock waiters or leak work.
- Timestamped history checks depend on obtaining a `SuperVersion` before validating collapsed history. Moving validation earlier can race with `full_history_ts_low` changes.
- Public option mutation must keep in-memory options, global timers, and OPTIONS files consistent under `options_mutex_`; slow persistence paths may release and reacquire DB mutex.
- `Close` and shutdown must avoid reentrant notifications, background error recovery races, and background tasks touching destroyed state.

## Test Signals

The header exposes extensive debug-only test hooks under `#ifndef NDEBUG`, including:

- Flush/WAL hooks: `TEST_SwitchWAL`, `TEST_SwitchMemtable`, `TEST_FlushMemTable`, `TEST_AtomicFlushMemTables`, `TEST_WaitForFlushMemTable`, `TEST_GetCurrentLogNumber`, `TEST_wals_total_size`, and `TEST_IsLogGettingFlushed`.
- Compaction hooks: `TEST_CompactRange`, `TEST_WaitForCompact`, `TEST_MaxNextLevelOverlappingBytes`, `TEST_BGCompactionsAllowed`, `TEST_BGFlushesAllowed`, `TEST_NumRunningBottomCompactions`, and manual mutex begin/end hooks.
- Recovery and background hooks: `TEST_IsRecoveryInProgress`, `TEST_GetBGError`, `TEST_WaitForBackgroundWork`, `TEST_WaitForPurge`, `TEST_DeleteObsoleteFiles`, and `TEST_UnableToReleaseOldestLog`.
- Metadata hooks: `TEST_Current_Manifest_FileNo`, `TEST_Current_Next_FileNo`, `TEST_GetFilesMetaData`, `TEST_GetLevel0TotalSize`, `TEST_GetLatestMutableCFOptions`, `TEST_table_cache`, and `TEST_GetAllBlockCaches`.
- Transaction/WAL prep hooks: `TEST_FindMinLogContainingOutstandingPrep`, `TEST_FindMinPrepLogReferencedByMemTable`, `TEST_PreparedSectionCompletedSize`, and `TEST_LogsWithPrepSize`.
- Periodic/stats/blob/file hooks: `TEST_WaitForPeriodicTaskRun`, `TEST_GetSeqnoToTimeMapping`, `TEST_GetFilesToQuarantine`, `TEST_EstimateInMemoryStatsHistorySize`, `TEST_GetFilesGrabbedForPurge`, `TEST_GetPeriodicTaskScheduler`, `TEST_ValidateOptions`, and `TEST_VerifyNoObsoleteFilesCached`.

Concrete behavioral tests should stress:

- WAL sync/rotation with `two_write_queues_`, manual WAL flush, `LockWAL`, failed sync, and closed-WAL manifest markers.
- Recovery from corrupted/old WAL records, WAL filters, 2PC prepared/unprepared batches, and retry open.
- Atomic flush across multiple column families and its MANIFEST installation ordering.
- Concurrent flush/compaction/purge scheduling with waits, pause/resume, abort, shutdown, and error recovery.
- Blob direct-write writes followed by reads before and after flush/manifest visibility.
- Timestamped reads around `full_history_ts_low` updates and collapsed history validation.
- File-deletion disabling/enabling, pending output preservation, external file ingestion rollback, and obsolete cache verification.
