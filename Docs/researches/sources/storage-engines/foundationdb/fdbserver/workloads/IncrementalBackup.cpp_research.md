# sources/storage-engines/foundationdb/fdbserver/workloads/IncrementalBackup.cpp

## Purpose
Backup-agent workload for submitting incremental backups, waiting for backup progress, optionally stopping backups, and restoring incremental backup data, including encrypted backup variants and system-key restore handling.

## Important APIs, types, and functions
`IncrementalBackupWorkload` owns backup URL/tag options, `FileBackupAgent`, mode flags (`submitOnly`, `restoreOnly`, `waitForBackup`, `stopBackup`, `checkBeginVersion`, `clearBackupAgentKeys`), optional blob manifest and encryption key file. It uses `addDefaultBackupRanges`, `IBackupContainer`, `BackupDescription`, `BackupContainerFileSystem`, `backupAgent.submitBackup`, `waitBackup`, `discontinueBackup`, and `restore`.

## Control flow
Only client 0 acts. `_start` computes backup ranges and configuration. Submit mode may create an encryption key file and submits an incremental-only backup, accepting duplicate-backup errors. Restore mode optionally clears file-backup system keys, waits for a backup container, optionally reads snapshot begin version from system keys, lists containers, splits restore ranges into normal and system ranges, restores system mutations first if needed, then restores normal ranges. `_check` can unpause backup agents, wait until contiguous log end reaches a read version, and discontinue the backup.

## State and persistence behavior
The workload writes backup-agent system metadata, backup container files under `backupDir`, optional encryption key files under `simfdb/`, and can clear `fileBackupPrefixRange`. Restore operations lock/unlock the database and may apply system mutation logs from `beginVersion`.

## Dependencies and integration points
Integrates with backup agent code, filesystem backup containers, encryption test utilities, management/system key ranges, database configuration, and restore locking.

## Risks and test signals
Risks include races while backup containers are being created, indefinite wait unless `waitRetries` bounds it, assumptions that `containers.front()` exists after listing, and destructive clearing/restoring of backup metadata. Signals are trace events for submit/wait/version-gate/restore phases, exceptions other than accepted duplicate or backup-unneeded errors, and successful completion of restore/check paths.
