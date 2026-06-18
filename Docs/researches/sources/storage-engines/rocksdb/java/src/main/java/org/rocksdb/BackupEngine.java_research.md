# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/BackupEngine.java

- **Purpose:** Java wrapper for RocksDB backup/restore engine operations.
- **Important APIs/types/functions:** Static `open(Env, BackupEngineOptions)` creates the native engine. Instance APIs include `createNewBackup`, `createNewBackupWithMetadata`, `getBackupInfo`, `getCorruptedBackups`, `garbageCollect`, `purgeOldBackups`, `deleteBackup`, `restoreDbFromBackup`, and `restoreDbFromLatestBackup`. JNI hooks perform all native work and `disposeInternalJni` releases the engine.
- **Control flow:** Callers open an engine from an environment and options, call backup/restore management methods, and close the wrapper. Backup creation optionally flushes memtables first and optionally attaches metadata. Restore methods pass backup ID/latest, target DB/WAL directories, and `RestoreOptions`.
- **State and persistence behavior:** Native backup engine manages backup directories, shared SST files, WAL inclusion, metadata, corrupted backup tracking, deletion, and restore output directories. Java state is just the native handle.
- **Dependencies:** Depends on `Env`, `BackupEngineOptions`, `RocksDB`, `RestoreOptions`, `BackupInfo`, `RocksObject`, `RocksDBException`, and native backup-engine JNI.
- **Integration points:** Used by application backup workflows and tests needing consistent database snapshots or backup pruning.
- **Risks:** Methods are documented as not thread-safe for backup creation. Restore from non-latest backups can conflict with shared table files if newer backups remain. Assertions guard ownership but are optional. Native filesystem failures surface as `RocksDBException`.
- **Test signals:** Open/close, backup with and without flush, metadata round-trip, corrupted-backup listing, garbage collection, purge/delete, restore latest/specific backup, and behavior with WAL-disabled writes.
