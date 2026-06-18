# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/BackupEngineTest.java

## Purpose
`BackupEngineTest` verifies end-to-end backup engine operations against temporary RocksDB instances.

## Important APIs and Types
Tests cover `createNewBackup`, `createNewBackupWithMetadata`, `deleteBackup`, `purgeOldBackups`, `restoreDbFromLatestBackup`, `restoreDbFromBackup`, `getCorruptedBackups`, `garbageCollect`, and `getBackupInfo`.

## Control Flow, State, and Persistence
Each test opens a temporary DB, writes known key/value pairs, creates backups under a temporary backup folder, and validates backup counts. Restore tests mutate DB values after backups, close the DB, restore from latest or selected backup, reopen the DB, and assert value suffixes reflect restored versions. `verifyNumberOfValidBackups` ensures no corrupted backups, runs garbage collection, and returns backup metadata.

## Dependencies and Integration Points
Depends on `Options`, `RocksDB`, `BackupEngineOptions`, `BackupEngine`, `RestoreOptions`, `BackupInfo`, `TemporaryFolder`, AssertJ, and `ThreadLocalRandom`.

## Risks and Test Signals
This is a strong integration signal for backup persistence, metadata, deletion, purge retention, and restore correctness. It also exercises filesystem cleanup and DB close/reopen ordering. It does not explicitly test WAL-disabled backup hazards described in `WriteOptions`.
