# sources/storage-engines/foundationdb/fdbclient/DatabaseBackupAgent.cpp

## Purpose

`DatabaseBackupAgent.cpp` implements FoundationDB's database-to-database DR backup agent orchestration. It owns task-bucket task functions for full range copy, mutation-log copy, differential backup, legacy upgrade/abort compatibility, status reporting, submit/discontinue/abort flows, and atomic switchover between source and destination clusters.

## Important APIs, Types, And Functions

`DatabaseBackupAgent` constructs subspaces under `databaseBackupPrefixRange` for `states`, `config`, `errors`, `ranges`, tag-name indexes, source-side state, a `TaskBucket`, and a `FutureBucket`. The source-taking constructor also sets `taskBucket->src`.

`DRConfig` stores newer per-DR metrics keyed by UID, notably `rangeBytesWritten()` and `logBytesWritten()`, and can clear its config subspace. `copyDefaultParameters()` propagates common task parameters: folder/backup UID, config log UID, destination UID, and add/remove prefixes. `checkTaskVersion()` rejects task versions newer than the task function supports and logs an error under the backup error subspace.

The registered task functions are the core execution graph:

- `BackupRangeTaskFunc` splits source key ranges on shard boundaries, reads committed source KV data, applies add/remove prefix mapping, writes destination keys, and records per-range version coverage in the apply-mutations key-version map.
- `FinishFullBackupTaskFunc` writes `copy_stop` at a source read version so log-copy work knows when full-copy catch-up can stop.
- `CopyLogRangeTaskFunc` streams mutation log ranges from source backup log keys into destination apply-log keys, batching by `BACKUP_LOG_WRITE_BATCH_MAX_SIZE`, prefetching with `COPY_LOG_PREFETCH_BLOCKS`, and breaking tasks by duration.
- `CopyLogsTaskFunc` repeatedly schedules `CopyLogRangeTaskFunc` slices and old-log erasure while advancing `applyMutationsEndRange`.
- `BackupRestorableTaskFunc` marks the backup restorable, then either schedules final cleanup for stop-when-done or starts differential log copying.
- `FinishedFullBackupTaskFunc` waits until apply has caught up, erases remaining log data, clears config/apply-log state, and marks the backup completed.
- `CopyDiffLogsTaskFunc`, `CopyDiffLogsUpgradeTaskFunc`, `OldCopyLogRangeTaskFunc`, `SkipOldEraseLogRangeTaskFunc`, and `AbortOldBackupTaskFunc` support differential mode and upgrade/abort paths for older task names and layouts.
- `StartFullBackupTaskFunc` initializes source mutation logging, destination UID mapping, begin versions, metadata version bumping, and schedules full-copy/log-copy/restorable tasks.

`DatabaseBackupAgentImpl` provides the public operation bodies: `submitBackup()`, `discontinueBackup()`, `abortBackup()`, `atomicSwitchover()`, `unlockBackup()`, `getStatus()`, `getStateValue()`, `getDestUid()`, `getLogUid()`, `waitUpgradeToLatestDrVersion()`, `waitBackup()`, and `waitSubmitted()`. The public `DatabaseBackupAgent` methods at the end delegate to these static helpers.

## Control Flow

Submission chooses or reuses a log UID, rejects existing runnable backups, coalesces requested ranges, optionally verifies or clears destination ranges, clears old config/state/errors, writes tag/config/state records, initializes apply-mutation version maps and prefix transforms, enqueues `dr_start_full_backup`, and locks or checks the database lock.

`StartFullBackupTaskFunc` then initializes the source-side destination UID and latest-version keys, writes destination-side begin version/config, enables source mutation logging for each backed-up range, bumps metadata version, and schedules parallel full-range copy and log-copy branches. The range-copy branch recursively splits on shard boundaries or restarts from `backupRangeBeginKey` when timeout/map-size pressure occurs. The log-copy branch continuously copies mutation log blocks, erases obsolete source log ranges, and advances apply boundaries until `copy_stop` is reached.

Abort first marks destination config as partially aborted and clears apply endpoints/logs using `COMMIT_ON_FIRST_PROXY` ordering to fence outstanding apply commits, then optionally cleans source-side mutation logs and finally marks the backup aborted. Atomic switchover validates status/locks/mutation stream IDs unless forced or simulated, locks the source, waits for destination apply to reach the lock commit version, stops destination backup, raises destination commit version if needed, starts reverse DR, waits for submission, and unlocks the old destination.

## State And Persistence

State is heavily persisted in FDB system-key subspaces. Destination-side state includes backup config, task-bucket tasks/futures, errors, status text, backup folder UID, DR version, prefix transforms, backup ranges, stop-when-done marker, apply-log keys, apply-mutation begin/end keys, and key-version maps/counts. Source-side state includes mutation log range registrations, destination UID lookup, backup latest-version keys, source status/folder ID, and source tag mapping. `DRConfig` persists byte counters separately under `uid->config`.

## Dependencies And Integration Points

This file depends on BackupAgent primitives, TaskBucket/FutureBucket, NativeAPI actors, management lock APIs, status client, key-backed types, system key encoders such as `applyMutations*`, `backupLogKeys`, `logRangesEncodeKey`, `destUidLookupPrefix`, and many `CLIENT_KNOBS` backup/log constants. It integrates source and destination databases, DR agents, mutation logging, apply-mutation machinery, cluster lock management, status JSON, and simulation probes.

## Risks And Test Signals

Important risks are ordering-sensitive abort/switchover commits, source/destination UID reuse, unbounded retries around non-retryable logical mistakes, legacy task compatibility, task version skew, key-version map growth throttling, and prefix transform correctness. `COMMIT_ON_FIRST_PROXY`, explicit conflict ranges, database-lock checks, byte locks, and task futures are key correctness mechanisms. Test signals should include full backup, stop-when-done completion, differential continuation, abort with and without source cleanup, DR upgrade from old task names, atomic switchover, prefix add/remove mappings, shard-split range copy, log-copy timeout continuation, and byte-counter reporting.
