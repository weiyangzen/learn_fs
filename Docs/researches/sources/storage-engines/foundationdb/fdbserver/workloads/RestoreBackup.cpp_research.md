# sources/storage-engines/foundationdb/fdbserver/workloads/RestoreBackup.cpp

## Purpose
`RestoreBackupWorkload` waits for an existing tagged backup to be usable, clears database and backup-system ranges, then restores the backup into the same cluster. It is a compact end-to-end restore consumer of backup-agent state.

## Important APIs, Types, And Functions
It derives from `TestWorkload` and registers as `RestoreBackup`. Important members are `FileBackupAgent backupAgent`, `Reference<IBackupContainer> backupContainer`, `backupDir`, `tag`, `delayFor`, `stopWhenDone`, and optional `encryptionKeyFileName`. Key actors are `waitOnBackup`, `clearDatabase`, and `_start`.

## Control Flow
Client 0 delays by `delayFor`, records a read version as a lower bound, waits for the backup tag, and handles either completed backups or running differential backups. For running differential backups with `stopWhenDone=false`, it polls the container description until contiguous log end reaches the captured read version, then discontinues the backup. It clears `normalKeys` and system backup ranges with system-key access and invokes `backupAgent.restore` with `WaitForComplete::True`, `LockDB::True`, and encryption parameters if a test encryption file exists.

## State And Persistence Behavior
The workload destroys current normal-key data and clears all system backup ranges before restore. It reads backup container metadata to determine log completeness. It may discontinue a running differential backup and may lock the database during restore.

## Dependencies And Integration Points
It depends on ManagementAPI, backup agent/container APIs, filesystem backup containers, simulator support, and test encryption utility helpers. It uses `getSystemBackupRanges()` to avoid leaving backup metadata in the restored cluster before applying backup contents.

## Risks And Edge Cases
The workload assumes an external backup has already been submitted. If the backup state is neither completed nor running differential, it emits `BadBackupState` and asserts. The captured read version gate avoids restoring a differential backup before it includes the desired point, but polling every five seconds can extend runtime under slow simulation.

## Test Signals
`BadBackupState`, `BackupVersionGate`, `DiscontinuingBackup`, and restore exceptions are the main signals. `check` always returns true; failures propagate through assertions or errors in `start`.
