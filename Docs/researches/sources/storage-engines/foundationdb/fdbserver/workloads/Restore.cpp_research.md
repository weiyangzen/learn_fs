# sources/storage-engines/foundationdb/fdbserver/workloads/Restore.cpp

## Purpose
`RestoreWorkload` validates backup-agent restore behavior from the most recent backup container for a selected tag. It optionally performs a restore, then checks backup-agent task queues and backup metadata/log subspaces for leftovers.

## Important APIs, Types, And Functions
The workload derives from `TestWorkload` and registers as `Restore`. Important state includes `backupTag`, `backupRanges`, `restoreRanges`, `LockDB locked`, `allowPauses`, `shareLogRange`, static `backupAgentRequests`, and a per-run `randomID`. Key actors are `changePaused`, `resumeAgent`, `statusLoop`, and `_start`. It uses `FileBackupAgent`, `BackupConfig`, `KeyBackedTag`, `BackupDescription`, `IBackupContainer`, `runRYWTransaction`, `getSystemBackupRanges`, `TaskBucket::debugPrintRange`, and simulation backup-agent policy state.

## Control Flow
Only client 0 runs. `_start` optionally toggles backup-agent pause state, starts a status loop, increments the static backup-agent request counter, resolves the backup tag to a log UID and container, and, when `performRestore` and a container exist, picks a target version from the container's restorable range. It clears backed-up ranges, filters restore ranges to exclude system backup ranges except normal-key intersections, and calls `backupAgent.restore` with a derived restore tag. After restore or no-restore operation, it waits for task count to drain and checks backup agent configuration keys, latest-version keys, and backup log value keys.

## State And Persistence Behavior
The workload clears `normalKeys` before restore and may restore only filtered normal-key ranges. It reads and validates system backup metadata under `logRangesRange`, `backupLatestVersionsPrefix`, and `backupLogKeys`. It can lock the database during restore, unlock afterward through restore parameters, and mutate simulation backup-agent policy when the final simulated request completes.

## Dependencies And Integration Points
It integrates deeply with FoundationDB's file backup agent, backup containers, task bucket metadata, system keyspace backup ranges, simulation policy state, and the tester workload runner. The `allowPauses` buggify path stresses backup-agent pause/resume while restore or status operations run.

## Risks And Edge Cases
The restore target version is randomized across min, max, an interior version, or latest restore. The leftover-key checks are sensitive to shared log ranges and to asynchronous task cleanup. Because the status loop and pause loop are not explicitly cancelled in `_start`, normal actor lifetime cancellation must clean them up. The static request counter must remain balanced across errors; exceptions rethrow after logging.

## Test Signals
Trace signals include `RW_Restore`, `RW_RestoreRanges`, `RW_CheckLeftoverTasks`, `BackupCorrectnessLeftOverMutationKeys`, `BackupCorrectnessLeftOverVersionKey`, `BackupCorrectnessLeftOverLogKeys`, and `RW_Complete`. The workload's `check` returns true, so errors are surfaced through assertions, thrown errors, and severe trace events during `_start`.
