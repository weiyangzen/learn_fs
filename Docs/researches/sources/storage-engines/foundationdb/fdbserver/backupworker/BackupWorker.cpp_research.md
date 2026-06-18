# sources/storage-engines/foundationdb/fdbserver/backupworker/BackupWorker.cpp

## Purpose
`BackupWorker.cpp` implements the classic log-router backup worker. A backup worker consumes mutation log messages for a backup tag, filters candidate mutations into configured backup key ranges, writes tagged mutation log files to backup containers, records byte counts and progress in system keys, and pops tlog data only when safe. It supports current-epoch workers and catch-up workers for older backup epochs after recovery.

## Important APIs, Types, and Functions
`VersionedMessage` wraps a `LogMessageVersion`, raw message bytes, tags, and arena ownership. `isThisMessageMutation()` skips special, transaction-system, log-protocol, span-context, and OTEL span-context messages before decoding a `MutationRef`. `isCandidateBackupMessage()` accepts normal keys, metadata version key, and allowed system backup mutations, including clear-range intersection with `systemBackupMutationMask()`.

`BackupData` is the worker state container. It tracks worker identity, tag, total tags, start and end versions, recruited and backup epochs, oldest backup epoch, known committed version, saved version, `LogSystemConsumer`, database handle, buffered messages, pause state, memory lock, active backups, triggers, counters, and logging. Its `PerBackupInfo` opens the backup container and ranges through `BackupConfig`, updates started-worker metadata for current-epoch workers, and tracks per-backup file progress.

Major actors and helpers include `shouldBackupWorkerExitEarly()`, `monitorBackupStartedKeyChanges()`, `monitorBackupProgress()`, `setBackupKeys()`, `saveProgress()`, `pullAsyncData()`, `uploadData()`, `saveMutationsToFile()`, `addMutation()`, `updateLogBytesWritten()`, `checkRemoved()`, `monitorWorkerPause()`, and the exported `backupWorker()`.

## Control Flow
`backupWorker()` constructs `BackupData`, starts displacement and failure monitors, starts progress monitoring on tag 0 for current epoch workers, starts pause monitoring, checks whether an old epoch can exit early, then starts pulling and uploading. Its main loop races DB-info changes, upload completion, and actor errors. DB-info changes rebuild a log-system consumer when backup pseudo-locality is available and update `oldestBackupEpoch`. Upload completion notifies the cluster controller with `BackupWorkerDoneRequest`.

`pullAsyncData()` waits while paused, opens or refreshes a log-router peek cursor, detects popped data, updates `minKnownCommittedVersion`, buffers peeked messages under a byte `FlowLock`, advances `pulledVersion`, trims messages beyond `endVersion`, and signals upload completion for bounded old epochs. `uploadData()` periodically finds a committed version boundary no later than `maxPopVersion()`, writes messages through `saveMutationsToFile()`, erases buffered messages, commits progress, updates `savedVersion`, and calls `pop()`.

`saveMutationsToFile()` waits for active backup containers and ranges, creates one tagged log file per active backup, builds a `KeyRangeMap` from backup ranges to file indexes, decodes and filters buffered mutations, splits clear ranges by backup-range intersection, writes records in block format via `addMutation()`, finishes files, updates per-backup `lastSavedVersion`, and atomically adds file sizes to `logBytesWritten`.

## State and Persistence Behavior
Progress is persisted under `backupProgressKeyFor(myId)` using `WorkerBackupStatus`. User-visible backup progress is stored in each `BackupConfig.latestBackupWorkerSavedVersion()` by tag 0 when all tags have reported the epoch and all workers have marked the backup started. `BackupConfig.startedBackupWorkers()` and `allWorkerStarted()` coordinate backup start acknowledgement. Log bytes are persisted through atomic adds to `BackupConfig.logBytesWritten()`.

The blob/container persistence path uses `IBackupContainer::writeTaggedLogFile(begin, end, blockSize, tagId, totalTags)`. Mutation records are big-endian `(version, subversion, messageSize, message)` entries inside blocks identified by `PARTITIONED_MLOG_VERSION`; padding uses `fileBackup::makePadding()`. Popping is deferred when older epochs still need data or during shutdown, preventing loss across recovery handoff.

## Dependencies and Integration Points
The worker integrates with `BackupAgent`, `BackupContainer`, `BackupConfig`, `BackupProgress`, `LogSystem`, `LogSystemConsumer`, `ServerDBInfo`, `WaitFailure`, `WorkerInterface`, system keys such as `backupStartedKey`, `backupPausedKey`, and `backupWorkerEnabledKey`, and trace/counter infrastructure. It is exported by `BackupWorker.h` and recruited through `BackupInterface` and `InitializeBackupRequest`.

## Risks and Test Signals
Correctness depends on writing only complete version boundaries and on not popping tlogs before durable progress is visible. `pullAsyncData()` logs an error for missing popped data but uses `ASSERT(true)`, which does not itself fail; callers depend on later behavior and trace visibility. Memory pressure is controlled by estimated message size and a lock capacity; an assertion fires if no messages can be processed while the lock has waiters. Backup start tracking only sets latest saved versions once all workers are ready, so stuck or removed workers can delay restorable progress. There are no local `TEST_CASE`s; primary signals are simulation/integration tests and traces such as `BackupWorkerMetrics`, `BackupWorkerSave`, `BackupWorkerSavedProgress`, and `BackupWorkerDone`.
