# sources/storage-engines/foundationdb/fdbserver/workloads/BackupWorkload.cpp

## Purpose
`BackupWorkload.cpp` defines the tester workload named `Backup`. It exercises FoundationDB's file backup path from simulation by submitting a backup over `normalKeys`, optionally using differential backup mode, pause/resume behavior, backup abort/discontinue paths, and test encryption-key files. A separate workload handles restore, so this file focuses on creating a restorable backup and validating the backup agent status path.

## Important APIs, Types, And Functions
The main type is `BackupWorkload : TestWorkload`, registered with `WorkloadFactory<BackupWorkload>`. It uses `FileBackupAgent`, `BackupAgentBase`, `IBackupContainer`, `BackupDescription`, `BackupContainerFileSystem::createTestEncryptionKeyFile`, `MutationLogType`, and `LockDB`. Key actors are `changePaused`, `resumeAgent`, `statusLoop`, `doBackup`, and `_start`.

## Control Flow
Only client 0 runs `start`. The constructor derives randomized timing options such as `backupAfter`, `restoreAfter`, `abortAndRestartAfter`, `differentialBackup`, and `stopDifferentialAfter`, then restricts backup ranges to `normalKeys`. `_start` may launch a pause toggler, creates an encryption key file when requested, waits for `backupAfter`, and calls `doBackup`. `doBackup` optionally aborts stale/duplicate backup state, submits a `file://simfdb/backups/` backup, runs a status loop, optionally waits until a differential backup is restorable before discontinuing or aborting, then waits for final backup completion.

## State And Persistence
Persistent effects are backup metadata in FDB system keys and backup files under the simulated filesystem. If encryption is enabled, a simulated encryption key file under `simfdb/` is created and passed to the backup agent. Workload state is otherwise in actor-local timing fields, backup tag/ranges, the pause actor, and trace events.

## Dependencies And Integration Points
The workload integrates with `fdbclient/BackupAgent.h`, backup containers, simulated filesystem backup containers, tester workload registration, `SERVER_KNOBS`, deterministic/nondeterministic randomness, and simulation backup-agent policy. It is meant to run with backup agents available and to coexist with a restore-oriented workload that consumes the produced backup.

## Risks
The status loop is intentionally infinite and relies on actor cancellation through owning futures. Randomized abort/discontinue paths can expose `backup_unneeded`, `backup_duplicate`, and `database_locked` races. Timing values must remain coherent; `stopDifferentialAfter` is computed relative to backup/abort/restore timing. Encryption tests depend on local simulated file setup. A local shadow variable named `minBackupAfter` means the member field is not populated, though the member is not subsequently used.

## Test Signals
Useful signals are `BW_Param`, `BW_DoBackupSubmitBackup`, `BW_DoBackupWaitForRestorable`, `BW_LastBackupContainer`, `BW_NotRestorable`, `BW_DoBackupComplete`, and `BackupCorrectness` errors. Successful workload `check` always returns true, so correctness is primarily encoded in trace/assert paths and later restore validation.
