# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/BackupInfo.java

- **Purpose:** Immutable Java value object describing one backup known to `BackupEngine`.
- **Important APIs/types/functions:** Package-private constructor takes backup ID, timestamp, size, file count, and application metadata. Public accessors are `backupId()`, `timestamp()`, `size()`, `numberFiles()`, and `appMetadata()`.
- **Control flow:** Instances are constructed from JNI when `BackupEngine.getBackupInfo()` materializes native backup metadata.
- **State and persistence behavior:** Stores a snapshot of backup metadata in final fields. It does not own native resources and does not mutate backup storage.
- **Dependencies:** References `BackupEngine` in javadoc; otherwise plain Java data.
- **Integration points:** Returned from backup listing APIs and used by applications/tests to inspect available backup IDs and metadata.
- **Risks:** No defensive validation; JNI must provide coherent values. `appMetadata()` may be null and callers must handle that.
- **Test signals:** Metadata values returned after creating backups, metadata null/non-null cases, file count/size consistency, and immutability expectations.
