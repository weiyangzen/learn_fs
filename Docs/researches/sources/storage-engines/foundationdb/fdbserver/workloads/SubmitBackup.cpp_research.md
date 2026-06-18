# sources/storage-engines/foundationdb/fdbserver/workloads/SubmitBackup.cpp

## Purpose
`SubmitBackupWorkload` submits a filesystem backup job from the tester. It is a management workload that exercises backup-agent submission paths, default backup ranges, optional encryption key setup, and duplicate backup handling.

## Important APIs, Types, and Functions
The workload wraps `FileBackupAgent::submitBackup()`, `addDefaultBackupRanges()`, `BackupContainerFileSystem::createTestEncryptionKeyFile()`, `StopWhenDone`, `IncrementalBackupOnly`, `MutationLogType::DEFAULT`, and encryption helpers from `TestEncryptionUtils`.

## Control Flow
The constructor reads backup directory, tag, delay, snapshot intervals, stop-when-done, incremental-only, and encrypted options. If encryption is enabled, it derives a simulation encryption key filename. `start()` runs only on client 0. `_start()` waits `delayFor`, constructs default backup ranges, creates the encryption key file if needed, and calls `submitBackup()`. `backup_duplicate` is logged and tolerated; other errors are rethrown.

## State and Persistence Behavior
Database state is the backup configuration/task state written by the backup agent. Filesystem state may include `simfdb/backups/` data and a test encryption key under `simfdb/`. No cleanup is performed by this workload. Backup tasks may outlive the workload depending on backup-agent behavior and `stopWhenDone`.

## Dependencies and Integration Points
It integrates with the FDB backup agent, backup container filesystem implementation, tester options, and encryption test helpers. Only the first client submits the backup to avoid intentional duplicate submissions.

## Risks and Edge Cases
The workload does not verify that the backup completes or restores correctly; it only submits. Duplicate backup errors are silently accepted, which is correct for idempotent simulation starts but can hide unexpected preexisting state. Encryption is random by default, so test coverage varies across deterministic seeds.

## Test Signals
`BackupSubmitError` is emitted for submission failures. `check()` always returns true, so external backup-agent traces and later backup workloads are needed to validate completion.
