# Research: sources/storage-engines/foundationdb/fdbclient/FileBackupAgent.cpp

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-008432`: lines 1-6359, `Docs/researches/chunks/subset-b-008432_research.md`
- `subset-b-008433`: lines 6360-8854, `Docs/researches/chunks/subset-b-008433_research.md`

## Chunk Research

### subset-b-008432: lines 1-6359

# sources/storage-engines/foundationdb/fdbclient/FileBackupAgent.cpp lines 1-6359

## Scope

This chunk covers the front and middle of FoundationDB's file backup agent implementation. It starts with helper state, restore configuration, backup file encoders/decoders, legacy backup abort compatibility, snapshot/log backup task functions, BulkDump snapshot integration, BulkLoad restore integration, range-file restore blocks, old-format mutation-log restore, partitioned-log conversion, and the beginning of non-partitioned restore dispatch. The requested range ends inside `RestoreDispatchTaskFunc::_finish()` at the point where it begins iterating restore files for a dispatch batch; the remainder of that task and the public `FileBackupAgent` wrapper methods are outside this chunk.

## Purpose

The code implements the task-bucket workflows that turn a FoundationDB backup configuration into external backup-container files and later restore those files back into a database. It supports three major data paths:

- Traditional range-file snapshots plus copied mutation-log files.
- Backup-worker partitioned logs, including restore-time merging of per-tag log streams into old backup mutation format.
- New BulkDump/BulkLoad snapshot acceleration, where snapshots are delegated to the BulkDump subsystem and restored through BulkLoad before mutation-log replay.

The implementation is actor-heavy and intentionally splits long-running work into durable `TaskBucket` tasks. Each task has an execute phase for external I/O or multi-transaction work and a finish phase for small, durable state updates.

## Important APIs, Types, and Functions

- Top-level helpers:
  - `monitorBulkDumpJobCompletion()` polls `getSubmittedBulkDumpJob()` until the submitted BulkDump job disappears or a timeout expires.
  - `verifyBulkDumpDatasetCompleteness()` verifies a `bulkdump_data/<job-id>/` directory exists and has files for filesystem backup containers.
  - `getBulkLoadTaskProgress()` scans `bulkLoadTaskPrefix` range-map entries, counts BulkLoad tasks by phase, and totals manifest bytes.
  - `monitorBulkLoadJobCompletionWithProgress()` polls a running BulkLoad job and periodically persists restore counters such as finished blocks, submitted/triggered/running tasks, total tasks, and bytes written.

- Restore configuration:
  - `RestoreConfig` extends `KeyBackedTaskConfig` under `fileRestorePrefixRange` and stores restore state, prefix translation, restore ranges, source container, versions, progress counters, file sets, BulkLoad flags, and apply-mutations coordination keys.
  - `RestoreConfig::RestoreFile` is the durable file descriptor ordered by `version` and `fileName`; it records whether a file is a range file or log file, block/file sizes, log end version, and partitioned-log tag metadata.
  - `getRestoreRangesOrDefault()` reads the newer `restoreRangeSet()` and falls back to older `restoreRanges()`/`restoreRange()` properties for compatibility.
  - `getProgress_impl()` and `getFullStatus_impl()` render restore status and add BulkLoad-specific phase details when `useRangeFileRestore` is false.

- File format support:
  - `fileBackup::RangeFileWriter` writes snapshot range blocks with a version header, begin/end keys, duplicated boundary KVs around block splits, and `0xff` padding.
  - `decodeRangeFileBlock()` and `decodeKVPairs()` validate headers, decode range-file blocks, and reject non-`0xff` trailing padding.
  - `fileBackup::LogFileWriter` writes old mutation-log blocks with `BACKUP_AGENT_MLOG_VERSION` headers and padded key/value records.
  - `decodeMutationLogFileBlock()` reads those log blocks for restore.
  - `getBackupContainerWithProxy()` reopens a backup container with the global `fileBackupAgentProxy`.

- Partitioned-log iterators:
  - `TwoBuffers` asynchronously pipelines fixed-size file reads across two buffers.
  - `PartitionedLogIteratorSimple` and `PartitionedLogIteratorTwoBuffers` read new partitioned-log backup files, skip block headers/padding, decode `VersionedMutation` records, and hide overlap between adjacent log files using stored end-version boundaries.
  - `endOfBlock()` treats `0xff` as block padding.

- Backup tasks:
  - `BackupRangeTaskFunc` writes snapshot range files for shard ranges, updates `snapshotRangeFileMap`, and recursively splits work on shard boundaries.
  - `BackupSnapshotDispatchTask` builds a shard map, subtracts already-dispatched ranges and out-of-backup ranges, dispatches range tasks according to snapshot schedule, and then either schedules another dispatch or `BackupSnapshotManifest`.
  - `BackupSnapshotManifest` walks the completed range-file map backwards to produce a non-overlapping snapshot manifest file and updates snapshot completion versions.
  - `BackupLogRangeTaskFunc` waits until its end version is readable, reads backup mutation-log key ranges, writes old-format log files, and splits large version spans.
  - `BackupLogsDispatchTask` advances continuous log backup, updates last restorable versions, dispatches log-copy tasks, erases old backup-log data, or polls when partitioned log modes are used.
  - `FileBackupFinishedTask` erases remaining log data, clears `backupStartedKey`, and marks a cleanly stopped backup completed.
  - `BulkDumpTaskFunc` submits or attaches to a BulkDump job, writes BulkDump snapshot metadata into the backup container, and persists `bulkDumpJobId`/BulkDump snapshot versions.
  - `StartFullBackupTaskFunc` enables backup workers if needed, records a begin version, starts mutation logging, initializes a snapshot, and schedules snapshot/log/finalization tasks according to snapshot mode.

- Restore tasks:
  - `BulkLoadRestoreTaskFunc` finds a BulkDump job id from task params or snapshot metadata, verifies the dataset, enables BulkLoad mode, submits a BulkLoad job, monitors it with progress, and marks the BulkLoad snapshot phase complete.
  - `RestoreCompleteTaskFunc` marks restore completed, bumps the metadata version, clears large restore maps, clears apply-mutation keys, and optionally unlocks the database.
  - `RestoreRangeTaskFunc` reads one range-file block, intersects it with requested restore ranges, applies prefix translation, clears/replaces target KV ranges, increments byte counters, and records original file ranges in the apply-mutations range map.
  - `RestoreLogDataTaskFunc` reads old-format log blocks, filters mutations against restore ranges, writes them under the restore `alog` prefix, and increments block/byte progress.
  - `RestoreLogDataPartitionedTaskFunc` groups partitioned log files by tag, merges per-tag iterators by commit version, converts new-format `VersionedMutation` records into old backup mutation KVs, and writes them under the restore mutation-log prefix.
  - `RestoreDispatchPartitionedTaskFunc` dispatches version batches for partitioned restore, including range-file block tasks, one partitioned-log conversion task, and the next dispatch task.
  - `RestoreDispatchTaskFunc` starts the non-partitioned dispatch state machine; in this chunk it handles apply-lag gating, empty-file completion decisions, batch future creation, and starts iterating files for block dispatch.

## Control Flow

Backup start begins with `StartFullBackupTaskFunc::_execute()`, which determines mutation log type, enables partitioned or range-partitioned backup workers, records the read version, and updates `backupStartedKey` so backup workers know the backup UID and begin version. Its finish phase starts default mutation logging for non-partitioned backups, creates encryption metadata in the backup container, sets the backup state to running, initializes snapshot metadata, and schedules the selected snapshot path plus continuous log dispatch and final cleanup.

Traditional snapshots flow from `BackupSnapshotDispatchTask` into many `BackupRangeTaskFunc` tasks. Dispatch constructs a `KeyRangeMap` of current shard boundaries, marks completed ranges from `snapshotRangeDispatchMap`, skips ranges outside `backupRanges`, calculates how many shards should have been dispatched by the next snapshot interval, and adds random not-done shard ranges to the task bucket. It deliberately avoids marking a snapshot finished in the same iteration that dispatched the final batch. Finish clears batch state, sets the dispatch-done future, and either schedules another dispatch at `nextDispatchVersion` or schedules `BackupSnapshotManifest` after the batch future.

`BackupRangeTaskFunc::_execute()` first splits itself if its input contains shard boundaries. Otherwise it streams committed KVs for its shard range through `readCommitted()`, writes one or more range files at read-version boundaries, and calls `finishRangeFile()` after each file. `finishRangeFile()` makes file creation durable by committing the range slice into `snapshotRangeFileMap`, updating byte/file counters, and advancing the task's begin key so retries continue from the correct point.

Mutation-log backup flows through `BackupLogsDispatchTask`. Each finish invocation advances `latestLogEndVersion`, updates last-restorable state, and either stops if `stopWhenDone` and restorable, schedules a `BackupLogRangeTaskFunc` plus the next dispatch task, or just polls when the backup is using partitioned logs. `BackupLogRangeTaskFunc` waits until the cluster read version exceeds its end version, optionally splits large log-range spans, copies backup-log records into a backup-container log file, and records file size so finish can add it to `logBytesWritten`.

BulkDump backup is a sibling snapshot path. `BulkDumpTaskFunc::_execute()` reads backup ranges and container URL, restores the original BulkDump mode from persisted config, attaches to an already submitted BulkDump job when present, otherwise enables BulkDump mode, creates a job rooted under `bulkdump_data`, submits it, and sets owner metadata. On success it verifies files exist under the job directory, writes a keyspace snapshot file containing BulkDump metadata rather than range files, restores BulkDump mode, and increments the test counter. Finish persists `latestSnapshotEndVersion`, `bulkDumpSnapshotEndVersion`, and `bulkDumpJobId`; in mode `BOTH` it avoids setting `firstSnapshotEndVersion` so range-file completion remains required before restorable state.

BulkLoad restore is a pre-log-replay snapshot path. `BulkLoadRestoreTaskFunc::_execute()` opens the backup container, reads restore ranges, discovers a missing `bulkDumpJobId` by scanning snapshot JSON metadata, verifies the BulkDump dataset, constructs a BulkLoad job for `normalKeys`, registers the BulkLoad range-lock owner, persists/restores the original BulkLoad mode, submits the job lock-aware because restore holds a database lock, and monitors completion while updating progress counters. Missing or incomplete BulkDump data is treated as permanent restore failure and sets restore state to aborted. Finish marks `bulkLoadComplete`, forces block progress counters to total, sets `firstConsistentVersion` if absent, signals its future, and finishes the task.

Range-file restore dispatches one `RestoreRangeTaskFunc` per block. Each block decode yields begin/end boundary keys plus real KVs. The task intersects the block range with every requested restore range, applies remove/add prefix mapping, clears the translated subrange, writes KVs with no write-conflict ranges, checks the restore database lock, and records bytes written. Finish maps the original backed-up key ranges to the snapshot version in `applyMutationsMapPrefix()` so later mutation application can tell which keys have a snapshot baseline.

Old-format log restore uses `RestoreLogDataTaskFunc`. It decodes a log block, groups multi-part mutation chunks by version with `AccumulatedMutations`, filters complete groups whose mutations do not intersect the target restore ranges, writes the remaining chunks under `restore.mutationLogPrefix()`, and lets the apply-mutations machinery consume them later. Partitioned-log restore instead uses `RestoreLogDataPartitionedTaskFunc`, which creates one iterator per tag, repeatedly finds the minimum next version, gathers all tag mutations for that version, converts them to old backup mutation KVs with `generateOldFormatMutations()`, batches by byte size, and writes to the same mutation-log prefix.

`RestoreDispatchPartitionedTaskFunc` advances version batches. It sets the apply end version for the previous batch, waits if apply lag is too high, gathers relevant log and range files for the next batch, queues all range-file block tasks, queues one partitioned-log conversion task, and schedules the next batch after the batch future. If it passes the restore version, it either schedules restore completion or requeues itself until apply lag reaches zero.

The non-partitioned `RestoreDispatchTaskFunc` follows the same batch principle. In the covered range it updates apply end version at batch boundaries, backs off on large apply lag, creates or reuses the batch future, handles empty-file cases by scheduling completion or a final apply-to-restore-version task, and begins the per-file loop that dispatches range/log blocks. The body after line 6359 is outside this chunk.

## State and Persistence Behavior

Durable state is primarily stored through `BackupConfig`, `RestoreConfig`, `TaskBucket`, and `FutureBucket` key-backed structures under system-key prefixes. Tasks carry config UIDs and task parameters, while completion dependencies are represented by future keys. Most execute phases do file I/O and multi-transaction work; finish phases commit small state transitions and set futures.

Backup state includes:

- Tag-to-UID mappings and abort flags through `KeyBackedTag`.
- `BackupConfig` fields such as backup ranges, destination UID, backup container, mutation log type, `stateEnum`, snapshot interval/version fields, snapshot dispatch maps, range-file map, log and range byte counters, last snapshot/log end versions, restorable version state, snapshot mode, BulkDump job id, original BulkDump mode, and worker-start markers.
- Cluster-level backup worker state through `backupStartedKey` and `backupPartitionRequiredKey`.
- Backup-container persistence through range files, log files, keyspace snapshot manifests, encryption metadata, and BulkDump metadata.

Restore state includes:

- `RestoreConfig` fields for restore UID/tag, source container URL/object, restore ranges, add/remove prefixes, restore target versions, first consistent version, batch future, progress counters, file sets, `applyMutationsBeginRange`/`applyMutationsEndRange`, `applyMutationsMapPrefix`, BulkLoad flags, original BulkLoad mode, and `unlockDBAfterRestore`.
- Range restore writes directly to user keyspace after clearing the target subrange, while log restore writes backup mutation chunks to the restore `alog` prefix for commit proxies to apply.
- `RestoreCompleteTaskFunc` clears large file/apply maps after completion and bumps `metadataVersionKey` to force clients to notice restored metadata changes.

Idempotence is an important design property. Range snapshot tasks persist begin-key advancement only after finishing a file. Restore block tasks use deterministic clear/set ranges and task futures. BulkDump and BulkLoad modes are persisted before task creation so retry after process failure can restore the previous DD mode. Existing BulkDump jobs are reused rather than blindly submitting duplicate jobs.

## Dependencies and Integration Points

- FoundationDB task framework: `TaskBucket`, `FutureBucket`, `TaskFuncBase`, `REGISTER_TASKFUNC`, task validation, task futures, scheduled versions, and task priorities.
- Key-backed configuration: `KeyBackedTaskConfig`, `KeyBackedProperty`, `KeyBackedSet`, `KeyBackedBinaryValue`, `krmSetRange()`, and `krmGetRanges()`.
- Backup container APIs: `IBackupContainer`, `BackupContainerFileSystem`, `IBackupFile`, `IAsyncFile`, keyspace snapshot files, encryption metadata, range/log file creation, file listing, and snapshot JSON metadata.
- Backup worker / mutation log APIs: `startMutationLogs()`, `eraseLogData()`, `getLogRanges()`, `backupStartedKey`, `enableBackupWorker()`, `enableRangeBackupWorker()`, partitioned log file metadata, and commit-proxy apply-mutations integration.
- BulkDump/BulkLoad APIs: `BulkDumpState`, `BulkLoadJobState`, `createBulkDumpJob()`, `submitBulkDumpJob()`, `getSubmittedBulkDumpJob()`, `setBulkDumpMode()`, `setBulkDumpOwner()`, `createBulkLoadJob()`, `submitBulkLoadJob()`, `getRunningBulkLoadJob()`, `setBulkLoadMode()`, `registerRangeLockOwner()`, `BulkLoadTaskState`, and `BulkLoadManifest` byte counts.
- Database management and locking: `ReadYourWritesTransaction`, system-key and lock-aware transaction options, `checkDatabaseLock()`, `unlockDatabase()`, `lockDatabase` expectations outside this chunk, `metadataVersionKey`, and DD/server-side mode knobs.
- Flow runtime: actors, `Future`, `PromiseStream`, `FlowLock`, `delay()`, `yield()`, `TraceEvent`, `buggify()`, and simulation-only failure/padding behavior.

## Risks and Edge Cases

- BulkLoad/BulkDump mode toggles are global DD-level state. The code persists original mode and restores it on success/error, but concurrent jobs or agents can still create ownership and mode-race hazards; BulkDump explicitly attaches to an existing job to reduce duplicate-submit conflicts.
- `verifyBulkDumpDatasetCompleteness()` only works for `BackupContainerFileSystem` and only checks that the job directory has files. It does not parse manifests, validate shard completeness, or support containers without listing.
- BulkLoad restore lacks client-side validation for server-side prerequisites such as SST ingestion support, shard-location metadata, and read-lock support. The code comments note that missing prerequisites can leave restores running with `0/0` tasks.
- Snapshot mode `BOTH` has subtle restorable-version semantics. `BulkDumpTaskFunc::_finish()` must not set `firstSnapshotEndVersion`; otherwise the backup can appear restorable before the range-file snapshot completes.
- Range-file and log-file formats rely on strict block sizing and `0xff` padding. Corrupted padding, short reads, unsupported file versions, or too-small block sizes raise restore/backup errors.
- Prefix translation during restore has boundary special cases around `allKeys.end` and `strinc(removePrefix)`. Incorrect handling can clear or write outside the intended translated range.
- Mutation-log filtering must keep incomplete multi-chunk mutation groups even if the visible partial data does not match a restore range; otherwise later chunks could be lost.
- Partitioned-log restore assumes per-tag files are continuous enough and versions advance monotonically. It logs severe events for missing tag IDs or non-continuous files, and iterator overlap skipping depends on correct file end-version metadata.
- Restore dispatch intentionally gates on apply lag. If commit proxies do not drain the restore `alog` prefix, dispatch tasks repeatedly requeue and restoration stalls.
- `RestoreDispatchTaskFunc` is split by this chunk boundary; analysis of actual non-partitioned per-file block dispatch, file-set cursor advancement, and subsequent task scheduling requires the next chunk.

## Test Signals

- BulkDump backup: submitting a BulkDump snapshot, reusing an already running job, restoring original BulkDump mode after success/error, writing BulkDump snapshot metadata, persisting `bulkDumpJobId`, rejecting empty/missing dataset directories, and `g_bulkDumpTaskCompleteCount` increments.
- BulkLoad restore: discovering `bulkDumpJobId` from snapshot metadata, aborting permanently when BulkDump metadata or files are missing, submitting a lock-aware BulkLoad job, updating submitted/triggered/running/total progress, restoring BulkLoad mode on timeout/error, marking `bulkLoadComplete`, and `g_bulkLoadRestoreTaskCompleteCount` increments.
- Backup snapshot dispatch: shard-map construction, backup-range skipping, already-dispatched range coalescing, randomized shard dispatch, `snapshotBatchFuture` cleanup, not finishing in the same iteration as final dispatch, and manifest generation after all shard tasks finish.
- Range file backup/restore: block-boundary duplication, padding validation, empty-range suppression, range-file map updates, restore clear/set batching, transaction-too-large backoff, original range-to-version map updates, and prefix translation at end boundaries.
- Log backup/restore: delayed reads until `endVersion` is readable, splitting large log spans, log byte accounting, old-format log block decode, mutation chunk completeness checks, range-based log filtering, and writes under restore mutation-log prefix.
- Partitioned restore: two-buffer iterator behavior across file/block boundaries, overlap skipping, per-tag merge ordering, old-format mutation generation by subsequence, apply-lag backoff, byte/block progress accounting, and batch chaining to restore completion.
- Compatibility and error handling: legacy 5.0/5.1 abort task aliases, unsupported task-version rejection, task validation failures, backup worker enablement for partitioned/range-partitioned logs, `backupStartedKey` cleanup, database lock checks during restore writes, and final database unlock behavior.

### subset-b-008433: lines 6360-8854

# sources/storage-engines/foundationdb/fdbclient/FileBackupAgent.cpp lines 6360-8854

## Scope

This chunk covers the tail of `RestoreDispatchTaskFunc`, restore status/abort helpers, the full-restore startup task, the `FileBackupAgentImpl` control-plane methods for backup/restore submission, waiting, status, pause, and atomic restore, the public `FileBackupAgent` forwarding methods, and a few fast-restore/blob-failure test helpers. Earlier task implementations for reading range/log blocks and applying mutations are outside this chunk, but this range is the orchestration layer that discovers restorable files, creates restore work, records status state, and exposes the public backup/restore API surface.

## Purpose

The code coordinates FoundationDB file backup and restore workflows through the task bucket and persistent `BackupConfig`/`RestoreConfig` metadata. Its main responsibilities are:

- Continue restore dispatch by splitting restore files into block tasks, preserving version-boundary batching so mutation logs are committed only after all range/log blocks for a batch finish.
- Report, wait for, and abort restores by reading restore tags and state keys under system-key and lock-aware transaction options.
- Start a full restore by validating state, forcing the destination cluster's read version above the target restore version, discovering the range/log files needed from the backup container, and persisting file metadata/counts into restore config maps.
- Decide the restore data path after startup: traditional range-file restore, partitioned-log dispatch, or BulkLoad-backed range restoration followed by mutation-log application.
- Submit backups and restores, normalize ranges, validate tag reuse, set up source/destination containers, persist options such as mutation-log type and snapshot mode, and enqueue the initial task.
- Provide user-facing status in text and JSON, including snapshot, mutation log, rangefile, BulkDump/BulkLoad compatibility, pause, lag, and recent error information.
- Implement control operations such as discontinue, abort, wait, pause/resume, worker disable checks, and correctness-only atomic restore.

## Important APIs, Types, and Functions

- `RestoreDispatchTaskFunc::_finish()` tail and `addTask()`:
  - Queues `RestoreRangeTaskFunc` or `RestoreLogDataTaskFunc` per file block.
  - Tracks `beginVersion`, `beginFile`, `beginBlock`, `batchSize`, and `remainingInBatch`.
  - Uses `TaskFuture` joining through `TaskCompletionKey::joinWith(allPartsDone)` so a dispatch batch completes only when all block tasks and any chained dispatch tasks finish.
  - Persists progress with `restore.filesBlocksDispatched().atomicOp(...)` and schedules the next dispatch or completion task.

- Restore helpers in `fileBackup`:
  - `restoreStatus(tr, tagName)` reads all restore tags or a single tag and returns `RestoreConfig::getFullStatus()`.
  - `abortRestore(tr, tagName)` marks runnable restores as `ERestoreState::ABORTED`, clears apply-mutation keys, cancels tag tasks, and unlocks the database.
  - `abortRestore(cx, tagName)` wraps the transactional abort retry loop and then commits a dummy conflict transaction to ensure mutation appliers have stopped submitting writes.

- `StartFullRestoreTaskFunc`:
  - `_execute()` validates `ERestoreState::QUEUED`/`STARTING`, clears stale file counters/maps, opens the backup container via `getBackupContainerWithProxy()`, discovers `RestorableFileSet`, writes log/range/all-file entries in transaction-sized chunks, and stores `firstConsistentVersion`.
  - `_finish()` transitions to `RUNNING`, initializes apply-mutation begin/end versions, chooses BulkLoad, partitioned-log, or standard dispatch, initializes incremental restore apply maps, and finishes the startup task.
  - `addTask()` binds a `RestoreConfig` UID to a `restore_start` task.

- `FileBackupAgentImpl`:
  - `waitBackup()` watches backup state until it is not runnable, or until differential mode is reached when `StopWhenDone` is false.
  - `submitBackup()` validates duplicate/runnable tags, enforces partitioned-log and range-partitioned-log mutual exclusion, creates the backup container, normalizes ranges, sets mutation-sharing destination UID metadata, persists `BackupConfig`, and enqueues `StartFullBackupTaskFunc`.
  - `submitRestore()` normalizes restore ranges, rejects duplicate/runnable restore tags, checks destination emptiness for traditional non-log-only restores, creates `RestoreConfig`, initializes mutation application, enqueues `StartFullRestoreTaskFunc`, and locks or verifies the database lock.
  - `waitRestore()` watches restore state and optionally prints progress every second while runnable.
  - `discontinueBackup()` either cancels an already restorable backup and marks it `STATE_COMPLETED`, or sets `stopWhenDone`.
  - `abortBackup()` cancels tasks, erases log data, clears backup start ID, and marks the config `STATE_ABORTED`.
  - `checkAndDisableBackupWorkers()` and `checkAndDisableRangeBackupWorkers()` disable worker roles when no matching partitioned backup remains.
  - `changePause()` writes both the task-bucket pause key and `backupPausedKey`.
  - `getStatusJSON()` and `getStatus()` build machine-readable and human-readable backup status.
  - `restore()` validates backup description/encryption, resolves target versions, verifies `getRestoreSet()`, submits restore, and optionally waits for completion.
  - `atomicRestore()` locks the source at a commit version, waits for the running backup to become restorable at or after that version, stops the backup, clears target ranges, and restores from the same backup URL under the same lock UID.

- Public `FileBackupAgent` methods:
  - `restore()` overloads adapt single-range, multi-range, and per-range begin-version arguments into `FileBackupAgentImpl::restore()`.
  - `atomicRestore()`, `abortRestore()`, `restoreStatus()`, `waitRestore()`, `submitBackup()`, `discontinueBackup()`, `abortBackup()`, status methods, `getLastRestorable()`, `setLastRestorable()`, `waitBackup()`, and `changePause()` forward into the implementation or `fileBackup` helpers.
  - `dataFooterSize` is defined as `20`.

- Test/support helpers:
  - `LogInfo` stores async log file metadata and an offset.
  - `insideValidRange()` checks whether a test key-value belongs to backup and restore ranges and logs trace details.
  - `writeKVs()` writes a slice of key-values and reads it back as a sanity check.
  - `simulateBlobFailure()` injects buggified blob-related failures such as HTTP request, connection, timeout, or lookup errors.

## Control Flow

Restore dispatch continues from previously loaded `RestoreConfig::fileSet()` entries. For each restore file, the dispatcher calculates block offsets from `beginBlock * blockSize`, queues a block task for range files or log files, and advances `beginBlock`, `blocksDispatched`, and `remainingInBatch`. If it finishes a file, it advances `beginFile` by appending `'\x00'` so later range scans resume after that file. If no blocks are dispatched, it either doubles `batchSize` when the queried files are too sparse/empty or chains another dispatch task into the existing batch future. When blocks were dispatched, it increments persistent block-dispatch counters, forces `remainingInBatch >= 1` if stopped mid-version, and schedules either an immediate same-batch dispatch or a follow-on dispatch that waits for `allPartsDone`.

Restore startup has an execute/finish split. `_execute()` first commits the state transition to `STARTING`, then separately ensures the destination read version exceeds `restoreVersion` by writing `minRequiredCommitVersionKey` as needed. It asks the backup container for a `RestorableFileSet`, converts range and log metadata into `RestoreConfig::RestoreFile` records, computes `firstConsistentVersion`, and writes log-file, range-file, and combined file maps in chunks capped around 1 MB of transaction payload. `_finish()` then switches the restore to `RUNNING`, initializes apply-mutation versions, and chooses downstream work: BulkLoad restore plus log dispatch when `useRangeFileRestore` is false, partitioned restore dispatch for `MutationLogType::PARTITIONED_LOG`, or normal `RestoreDispatchTaskFunc`.

Backup submission is a single transactional setup path. It rejects active duplicate tags, removes old non-runnable config, checks mutation-log-type conflicts, creates or opens the destination container, normalizes backup ranges through `KeyRangeMap`, assigns mutation-sharing destination UID metadata, persists config fields, points the tag to the new UID, and schedules the first full-backup task. Restore submission follows the same tag/config pattern but also validates destination emptiness for traditional restores, initializes apply-mutation prefix handling, and locks or validates the database lock using the restore UID.

Waiting and status paths are watch-driven. `waitBackup()` watches `BackupConfig::stateEnum().key`; `waitRestore()` watches `RestoreConfig::stateEnum().key`, with optional progress printing and a one-second delay race for verbose output. Status generation performs one retryable read transaction, collects version/timestamp information through timekeeper helpers, and formats either JSON fields or CLI text.

Atomic restore is a correctness workflow: require the backup to be in `STATE_RUNNING_DIFFERENTIAL`, lock the database and capture the lock commit version, wait until the backup has a latest restorable version at least that high, discontinue and wait for the backup to stop, clear target ranges, then invoke the normal restore path using the backup container URL and the same lock UID.

## State and Persistence Behavior

- Restore task parameters persist in task metadata: `beginVersion`, `beginFile`, `beginBlock`, `batchSize`, `remainingInBatch`, and `StartFullRestoreTaskFunc::Params::firstVersion`.
- Restore config state includes `stateEnum`, `restoreVersion`, `firstConsistentVersion`, `beginVersion`, `onlyApplyMutationLogs`, `inconsistentSnapshotOnly`, `unlockDBAfterRestore`, `mutationLogType`, `useRangeFileRestore`, `sourceContainer`, restore ranges, apply-mutation prefixes/maps, batch future key, file maps, and counters such as file count, file-block count, and blocks dispatched.
- File discovery persists three views: `logFileSet()`, `rangeFileSet()`, and combined `fileSet()`. The combined map drives dispatch ordering; the specialized maps preserve log/range metadata for other restore behavior.
- Backup config state includes tag, state enum, backup container, stop-when-done flag, normalized ranges, snapshot intervals, mutation log type, incremental-only flag, snapshot mode, destination UID value, latest-version metadata, byte counters, error maps, BulkDump job ID, and BulkDump progress integration.
- Tag state is stored via `KeyBackedTag` mappings from user tags to `{ UID, aborted flag }`. Both backup and restore submission replace tag pointers only after validating old runnable state.
- Database lock state is part of restore correctness. Normal restore may lock or verify a lock by UID; abort unlocks using the restore UID; atomic restore reuses a generated UID across lock, optional system restore, user restore, and final unlock.
- Worker pause state is duplicated intentionally: the task bucket pause key controls backup-agent tasks, while `backupPausedKey` controls backup workers.
- `lastRestorable` is stored under a `FileBackupAgent` keyspace by tag and encoded as a `Version`.

## Dependencies and Integration Points

- FoundationDB transaction APIs: `ReadYourWritesTransaction`, `Transaction`, `runRYWTransaction`, transaction options for system keys, lock-aware reads/writes, immediate priority, and commit-on-first-proxy.
- Task infrastructure: `TaskBucket`, `FutureBucket`, `Task`, `TaskFuture`, `TaskCompletionKey`, `REGISTER_TASKFUNC`, task priorities, task cancellation through tags, and `keepRunning()` leases.
- Backup container APIs: `IBackupContainer::openContainer()`, `create()`, `describeBackup()`, `getRestoreSet()`, `getURL()`, `getProxy()`, encryption block-size handling, and proxy wrapping.
- Restore/backup config wrappers: `RestoreConfig`, `BackupConfig`, key-backed tags/maps/sets, range maps, and helpers such as `getAllRestoreTags()`, `makeRestoreTag()`, `makeBackupTag()`, `krmSetRange()`, and `eraseLogData()`.
- BulkLoad/BulkDump integration: `BulkLoadRestoreTaskFunc::addTask()`, `getBulkLoadMode()`, `originalBulkLoadMode()`, `bulkDumpJobId()`, `getBulkDumpProgress()`, `BulkDumpProgress`, and snapshot modes `rangefile`, `bulkdump`, and `both`.
- Mutation-log worker integration: `MutationLogType`, partitioned/range-partitioned backup detection, `enable/disable` worker helpers, `backupPartitionRequiredKey`, and dispatch variants for partitioned logs.
- Time/status integration: timekeeper version-to-epoch helpers, formatting helpers for durations, bytes, timestamps, versions, JSON builders, and trace events.
- CLI/user workflows integrate through public `FileBackupAgent` methods used by `fdbbackup`/`fdbrestore`, including wait/verbose behavior and printed error messages for encryption, destination, and container failures.

## Risks and Edge Cases

- Restore batching must not end mid-version when range files and log files overlap a version. The `beginFile`/`remainingInBatch` logic is the main guard; an error here can allow logs to apply before all snapshot/range blocks for the same version finish.
- Sparse or empty restore files can cause no block tasks to be dispatched. The code doubles `batchSize` when no files were consumed and otherwise treats it as empty-file progress, avoiding a tight loop but risking very large batches if metadata is unexpectedly sparse.
- `StartFullRestoreTaskFunc::_execute()` writes large file lists in approximately 1 MB chunks, but comments note that very large file sets can still stress value/transaction limits because file-set metadata can be large.
- BulkLoad restore intentionally skips destination-empty checks because DD range-lock overwrite is expected. Incorrectly selecting `useRangeFileRestore=false` could overwrite existing ranges that traditional restore would reject.
- Encryption validation is strict: encrypted backups require a key file, and unencrypted backups reject a provided key file. Container caching requires explicitly resetting the encryption block size after reopening.
- Blobstore backup description uses `invalidVersion` to tolerate eventually consistent metadata. Restore version validation still depends on `getRestoreSet()` returning a complete set.
- Backup mutation-log types `PARTITIONED_LOG` and `RANGE_PARTITIONED_LOG` are mutually exclusive at submission time because worker recruitment depends on active non-default type.
- Status JSON currently builds error objects but does not push them into `errorList` in the shown code, so JSON `Errors` may remain empty even when errors were read.
- Atomic restore assumes a running differential backup, waits by polling every 0.2 seconds for a restorable version, and clears destination ranges before normal restore; failures after clearing but before restore completion leave the database locked/cleared until higher-level recovery handles it.
- `writeKVs()` assumes `begin` is valid when reading `kvs[begin]`; callers must not pass an out-of-range empty slice except the code only tolerates `begin == end` after forming the range.
- `simulateBlobFailure()` injects random transient errors only under `buggify()`, so tests must tolerate nondeterministic failure paths in simulation.

## Test Signals

- Restore dispatch: files with zero size, multiple blocks, mid-file continuation, mid-version stopping, overlapping range/log versions, batch-size exhaustion, `RESTORE_DISPATCH_ADDTASK_SIZE` under buggify, and `filesBlocksDispatched` increments.
- Restore lifecycle: status on no tags, status on all tags, abort of missing/runnable/non-runnable restores, clearing apply-mutation keys, task cancellation, unlock behavior, and dummy transaction after abort.
- Full restore startup: queued-to-starting transition, unexpected old state error logging, destination version forcing via `minRequiredCommitVersionKey`, missing restore data, logs-only restore, inconsistent-snapshot-only restore, first-consistent-version calculation, and transaction chunking for large file metadata sets.
- Restore path selection: BulkLoad restore creates a `BulkLoadRestoreTaskFunc`, persists original BulkLoad mode, switches to log-only dispatch after BulkLoad, partitioned-log dispatch uses version batches, and traditional restore queues normal dispatch.
- Backup submission: duplicate active tag rejection, old completed config clearing, local `file://` URL timestamp suffixing, container create failure, last-backup timestamp in the future, range normalization/coalescing, mutation-sharing UID reuse, snapshot mode persistence, and partitioned/range-partitioned conflict messages.
- Restore submission: duplicate UID/tag handling, destination-not-empty rejection for traditional restore, validation-prefix exception, BulkLoad destination precheck skip, restore range prefix assertions, lock versus check-lock paths, begin-version persistence, and apply-mutation initialization.
- Waiting and status: watch wakeups on backup/restore state changes, verbose restore progress cadence, paused agent reporting, text/JSON snapshot modes, BulkLoad compatibility, BulkDump progress/stalled task fields, lag calculations, and recent versus older error grouping.
- Backup controls: discontinue before/after latest restorable version exists, `stopWhenDone` duplicate behavior, abort cleanup of log data and backup start ID, worker-disable calls when no partitioned backups remain, and range-partition cleanup marker write.
- Atomic restore: requires `STATE_RUNNING_DIFFERENTIAL`, captures a lock commit version, waits for restorable version to catch up, handles discontinue races, clears requested ranges, and restores with the same lock UID.
- Public wrappers: overload behavior for default backup ranges, per-range versus uniform begin versions, optional lock UID generation, `setLastRestorable()` encoding, and forwarding consistency for backup/restore status/control methods.
