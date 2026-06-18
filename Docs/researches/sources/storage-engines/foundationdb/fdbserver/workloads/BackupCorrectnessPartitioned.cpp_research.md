# sources/storage-engines/foundationdb/fdbserver/workloads/BackupCorrectnessPartitioned.cpp

Purpose: defines `BackupAndRestorePartitionedCorrectness`, a file-backup variant that restores selected ranges as partitioned work. It is close to `BackupCorrectness.cpp` but emphasizes splitting user and system ranges, restoring multiple normal ranges, and verifying that skipped ranges remain absent.

Important APIs, types, and functions: `BackupAndRestorePartitionedCorrectnessWorkload` extends `TestWorkload`. Constructor options mirror the main file-backup workload: timing knobs, backup tag, backup-range generation, differential mode, pause allowance, shared log ranges, default backup, restore prefix filtering, and optional encryption. Helpers include `changePaused()`, `statusLoop()`, `doBackup()`, `clearAndRestoreSystemKeys()`, `_start()`, and `_check()`.

Control flow: client 0 optionally adds system backup ranges, starts and possibly pauses backup-agent tasks, creates an encryption key if configured, delays until backup start, runs `doBackup()`, waits for backup completion or allowed database-lock failure, reads backup metadata and container, waits for restore time, clears backup ranges, selects a target restorable version, separates system ranges from normal ranges, restores system ranges first, then launches one restore per selected normal range using distinct restore tags. It waits for all restore futures, then checks backup task/config/log/latest-version cleanup.

State and persistence behavior: backup metadata and mutation logs are in the same file-backup system keyspaces as `BackupCorrectness.cpp`, with destination UID paths derived from `BackupConfig(logUid)`. Restore state is spread across tags named from the backup tag plus range index. Skipped ranges are kept in `skippedRestoreRanges` and verified by `_check()`.

Dependencies and integration points: depends on `FileBackupAgent`, `TaskBucket`, `IBackupContainer`, `BackupContainerFileSystem`, encryption test support, `DatabaseConfiguration`, simulator backup-agent policy state, and system backup ranges. It disables `RandomRangeLock`.

Risks and edge cases: because each normal range may become an independent restore, failures can be partial and must be diagnosed per restore tag. System-key ranges require special clear-and-restore handling before normal ranges. Like the main workload, cleanup polling can be slow, and `check()` does not compare restored data byte-for-byte. Prefix filtering or random skipped ranges can produce empty restore ranges, so constructor assertions and fallback behavior matter.

Test signals: failures are visible through severe traces such as `BARW_UnexpectedRangePresent`, `BARW_NotRestorable`, `BackupCorrectnessLeftOverMutationKeys`, `BackupCorrectnessLeftOverVersionKey`, `BackupCorrectnessLeftOverLogKeys`, and top-level `BackupAndRestorePartitionedCorrectness`.
