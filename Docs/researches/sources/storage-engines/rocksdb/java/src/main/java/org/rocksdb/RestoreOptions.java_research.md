# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/RestoreOptions.java

## Purpose
`RestoreOptions` is the Java owning wrapper for native `rocksdb::RestoreOptions`, used by `BackupEngine` restore operations. Its exposed configuration controls whether existing WAL/log files are preserved during restore.

## Important APIs, Types, And Functions
- Constructor `RestoreOptions(boolean keepLogFiles)` allocates native restore options.
- Native `newRestoreOptions(boolean)` constructs `ROCKSDB_NAMESPACE::RestoreOptions`.
- `disposeInternal(long)` deletes the native restore options through `disposeInternalJni`.

## Control Flow
Callers construct `RestoreOptions`, pass it into `BackupEngine.restoreDbFromBackup` or `restoreDbFromLatestBackup`, and close it when done. JNI restore methods consume the native handle and native RocksDB applies `keep_log_files` semantics.

## State And Persistence Behavior
The object owns one native restore-options allocation. `keepLogFiles` is set only at construction and no Java getter/setter exists. The option affects restored filesystem state: when true, restore does not overwrite existing WAL files and moves archived logs to the WAL directory, which is useful with backup configurations that do not back up log files.

## Dependencies And Integration Points
- Extends `RocksObject`.
- Used by `BackupEngine` restore APIs.
- JNI implementation is in `java/rocksjni/restorejni.cc` and includes `rocksdb/utilities/backup_engine.h`.
- Java tests in `BackupEngineTest` construct `RestoreOptions(false)` for restore paths.

## Risks And Edge Cases
- Java exposes only construction-time configuration; callers needing to inspect or toggle `keepLogFiles` must create a new object.
- Misusing `keepLogFiles=true` can retain WAL files inconsistent with the restored backup if the backup/log-file policy is not understood.
- As with other `RocksObject` wrappers, failing to close leaks native memory.

## Test Signals
- `BackupEngineTest` covers restore calls with `RestoreOptions(false)`.
- Additional coverage for `keepLogFiles=true` would be valuable, especially when `BackupEngineOptions.backup_log_files=false` is involved.
