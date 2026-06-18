# sources/storage-engines/rocksdb/db/db_impl/db_impl_open.cc

## Purpose

`db_impl_open.cc` implements normal RocksDB DB opening and recovery. It sanitizes and validates options, creates brand-new DB metadata, locks and recovers existing DBs, replays MANIFEST and WAL files, flushes recovered memtables when needed, creates the next writable WAL, persists recovery edits/options/identity, initializes hidden persistent-stats state, schedules cleanup/background work, supports async WAL precreation and async table-file opening, and exposes `DB::Open`/`DB::OpenAndTrimHistory` entry points.

## Important APIs, Types, And Functions

- `SanitizeOptions` normalizes DB/CF options, creates default objects, adjusts thread pools, WAL recycling/compression, WAL/db paths, rate limits, and SST file manager defaults.
- `DBImpl::ValidateOptions` and the file-local `ValidateOptionsByTable` reject incompatible DB/CF options.
- `DBImpl::NewDB` creates MANIFEST-000001, writes the initial `VersionEdit`, syncs it, and writes `CURRENT`.
- `DBImpl::CreateAndNewDirectory` and `Directories::SetDirectories` create/open DB, WAL, and data directories.
- `DBImpl::Recover` is the main manifest/WAL recovery routine used by read-write and read-only open paths.
- Persistent stats helpers: `InitPersistStatsColumnFamily` and `PersistentStatsProcessFormatVersion`.
- Recovery edit/filter helpers: `LogAndApplyForRecovery`, `InvokeWalFilterIfNeededOnColumnFamilyToWalNumberMap`, and `InvokeWalFilterIfNeededOnWalRecord`.
- WAL replay pipeline: `RecoverLogFiles`, `SetupLogFilesRecovery`, `ProcessLogFiles`, `ProcessLogFile`, `InitializeLogReader`, `ProcessLogRecord`, `InitializeWriteBatchForLogRecord`, `InsertLogRecordToMemtable`, `MaybeWriteLevel0TableForRecovery`, `HandleNonOkStatusOrOldLogRecord`, `UpdatePredecessorWALInfo`, `FinishLogFileProcessing`, `MaybeHandleStopReplayForCorruptionForInconsistency`, `MaybeFlushFinalMemtableOrRestoreActiveLogFiles`, `GetLogSizeAndMaybeTruncate`, `RestoreAliveLogFiles`, and `WriteLevel0TableForRecovery`.
- Open entry points: `DB::Open`, `DB::OpenAndTrimHistory`, and `DBImpl::Open`.
- WAL creation and async helpers: `CreateWALWriter`, `StartWALFile`, `CreateWAL`, `AsyncWALPrecreateEnabled`, `MaybeScheduleAsyncWALPrecreate`, `WaitForAsyncWALPrecreate`, and `BGWorkAsyncWALPrecreate`.
- Async file-open helpers: `ScheduleAsyncFileOpening`, `MarkAsyncFileOpenNotNeeded`, and `BGWorkAsyncFileOpen`.

## Control Flow

`DB::Open` converts `Options` into DB/CF descriptors, optionally adds the hidden persistent-stats CF, sets thread tracking, and calls `DBImpl::Open`, retrying once when manifest read corruption can be reconstructed by the filesystem. `DBImpl::Open` validates options, creates directories and archival directory, constructs `DBImpl`, locks `options_mutex_` and `mutex_`, and calls `Recover`.

`Recover` handles the persistent metadata phase. In read-write mode it creates directories, locks `LOCK`, checks `CURRENT` or, in best-efforts mode, searches for a non-empty MANIFEST, creates a new DB if allowed, checks `error_if_exists`, and verifies filesystem/direct-I/O compatibility. It then recovers the `VersionSet` from MANIFEST or best-efforts `TryRecover`, possibly records trivial LSM moves for dynamic-level migration, reconciles/persists DB ID, updates next file number, creates CF directories, and scans WAL files. WAL verification can require tracked WALs in MANIFEST to match the directory; disabling manifest WAL tracking emits a safety edit deleting old tracked WAL state. It enforces read-only flags that reject non-empty WALs when requested, then sorts and replays WALs through `RecoverLogFiles`.

The WAL replay pipeline starts with `SetupLogFilesRecovery`, which creates per-CF `VersionEdit`s, logs a recovery-started event, invokes the WAL filter with the CF-to-log map, and computes the minimum WAL to keep. `ProcessLogFiles` iterates sorted WAL numbers and calls `ProcessLogFile`. Each WAL is marked used, opened through `InitializeLogReader`, then records are read in a loop. `ProcessLogRecord` decodes the write batch, reconciles timestamp-size differences, updates protection info/checksums, validates sequence numbers, allows a `WalFilter` to ignore/modify/stop/corrupt the record, inserts valid writes into memtables, and may flush scheduled memtables to L0 during recovery. After each WAL, predecessor metadata is updated, corruption/old-record handling applies the configured `WALRecoveryMode`, sequence numbers are published, and final recovery either flushes remaining memtables, records log-number edits, emits WAL deletion/min-log edits, restores active log files for `avoid_flush_during_recovery`, or truncates preallocated WAL tail space.

`WriteLevel0TableForRecovery` flushes a recovered memtable under the DB open path. It reserves a pending output number, builds a level-0 table and possible blob files with `BuildTable`, verifies memtable/output counts when configured, fsyncs the data directory before publishing the edit, adds file/blob additions to the `VersionEdit`, handles user-defined timestamp history cutoff movement, updates compaction/flush stats, and releases the pending output.

After `Recover`, `DBImpl::Open` creates a new writable WAL, optionally writes and syncs an empty batch at a recovered PIT sequence boundary, logs and applies all recovery edits, removes obsolete identity if identity-file writing is disabled, initializes persistent stats, prepopulates sequence-time mapping for new DBs, creates requested column-family handles or missing CFs, initializes blob direct write, installs superversions, validates memtable capabilities, writes an OPTIONS file, marks the DB opened, tracks existing files with `SstFileManager`, cleans trash and obsolete files, schedules flush/compaction, async file opening, async WAL precreation, syncs any buffered WAL header/dummy data, starts periodic tasks, registers seqno-time workers, and finally publishes the `unique_ptr<DB>`.

`DB::OpenAndTrimHistory` wraps `DB::Open`, rejects `avoid_flush_during_recovery`, force-compacts timestamp-enabled CFs at the trim timestamp, and cleans up handles/DB on failure.

## State And Persistence Behavior

This file creates and mutates the core durable state: `CURRENT`, MANIFEST/version edits, WAL files, `IDENTITY`, OPTIONS files, recovered L0 SST/blob files, tracked WAL metadata, min-log retention, per-CF log numbers, DB/session IDs, persistent stats CF keys, and sequence/time metadata. It carefully alternates mutex-held metadata updates with unlocked IO-heavy work. Recovery edits are accumulated in `RecoveryContext` and atomically persisted through `VersionSet::LogAndApply`.

Runtime state initialized here includes `db_lock_`, `default_cf_handle_`, `persist_stats_cf_handle_`, `logs_`, `alive_wal_files_`, `cur_wal_number_`, `min_wal_number_to_recycle_`, write-buffer recovery thresholds, flush/trim schedulers, superversions, thread-status CF info, error-handler auto-recovery, SST file manager tracking/reserved disk buffer, async WAL precreate state, and async file-open state.

## Dependencies And Integration Points

The file integrates with almost every DBImpl subsystem: `VersionSet`, `ColumnFamilyData`, `Manifest`, `WriteBatchInternal`, memtables, `BuildTable`, blob file additions, WAL reader/writer and compression/tracking, `WalFilter`, `SstFileManagerImpl`, `DeleteScheduler`, persistent stats history, sequence-time workers, table cache preopening, thread status, rate limiter, Env/FileSystem, options sanitation, and event logging. It also interacts with read-only open through `Recover(read_only=true)` and with `db_impl_files.cc` through DB identity, next-file-number updates, obsolete cleanup, and WAL retention.

## Risks And Edge Cases

- Recovery ordering is delicate: files must be durable before MANIFEST edits reference them, new WAL headers/dummy PIT records must be synced, and recovery edits must be applied before public DB exposure.
- WAL recovery mode differences are subtle. `kPointInTimeRecovery`, `kSkipAnyCorruptedRecords`, `kTolerateCorruptedTailRecords`, and `kAbsoluteConsistency` produce different replay stop/fail behavior.
- WAL filters can change batches but must not increase record count; bad filter behavior can corrupt recovery semantics.
- Timestamp-size reconciliation and user-defined timestamp stripping affect both WAL replay and recovery flush output.
- `avoid_flush_during_recovery` preserves active WALs instead of flushing everything, which complicates WAL liveness and future deletion.
- Best-efforts recovery ignores normal `CURRENT` assumptions and must still rebuild enough metadata safely.
- Async WAL precreation and async file opening publish background results through shared DB state and must handle shutdown/failure races.
- Dynamic-level trivial moves during open are persisted only if recovery succeeds; incorrect edits can reshape the LSM unexpectedly.
- Persistent stats CF recreation uses normal write paths while open is still in progress, so lock transitions and hidden-handle state matter.

## Test Signals

Important tests include new DB creation and manifest/CURRENT sync, open retry with verify-and-reconstruct reads, best-efforts recovery, direct-I/O compatibility failure, WAL tracking in MANIFEST, missing/extra WAL handling, all WAL recovery modes, WAL filter modify/ignore/stop/corrupt cases, timestamp-size WAL replay, recovered memtable flush with blob additions, `avoid_flush_during_recovery`, PIT dummy write/sync, DB ID/IDENTITY combinations, persistent stats format migration, create-missing-CF open, dynamic-level trivial move migration, async WAL precreate hit/miss/failure, async file-open errors, and crash tests around recovery edit persistence. The file exposes many `TEST_SYNC_POINT` hooks for WAL replay, flush, manifest optimization, async WAL precreate, async open, and final open sequencing.
