<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/backupenginejni.cc -->
# Research: sources/storage-engines/rocksdb/java/rocksjni/backupenginejni.cc

Purpose: Implements JNI bindings for Java `BackupEngine`, forwarding Java backup and restore operations to C++ `ROCKSDB_NAMESPACE::BackupEngine`.

Important APIs/types/functions: Native methods include `open`, `createNewBackup`, `createNewBackupWithMetadata`, `getBackupInfo`, `getCorruptedBackups`, `garbageCollect`, `purgeOldBackups`, `deleteBackup`, `restoreDbFromBackup`, `restoreDbFromLatestBackup`, and `disposeInternalJni`.

Control flow: `open` converts env/options handles and calls `BackupEngine::Open`, returning a native pointer or throwing `RocksDBException`. Backup/restore calls reinterpret DB/engine/options handles, convert Java strings to C strings or std::string, invoke C++ methods, release JNI strings, and throw Java exceptions on non-OK `Status`. Info methods convert C++ vectors into Java lists or int arrays.

State and persistence behavior: The native `BackupEngine` handle owns backup engine state until deleted. Operations create backup files, metadata, garbage-collect obsolete data, delete backup ids, and restore DB/WAL directories according to C++ backup engine semantics.

Dependencies and integration points: Depends on generated JNI headers, backup engine utilities, `RocksDBExceptionJni`, `BackupInfoListJni`, Java `DB`, `Env`, `BackupEngineOptions`, and `RestoreOptions` handles.

Risks and edge cases: Backup IDs are converted to `jint`, with a comment acknowledging possible precision loss from wider native ids. JNI string acquisition failures must release already-acquired strings, which restore paths handle. Java-side handle lifetime must ensure DB/options/env remain valid during calls.

Test signals: `BackupEngineTest` should cover open failure propagation, backup creation with/without metadata, corrupted backup list conversion, purge/delete, restore by id/latest, and native handle disposal under `-Xcheck:jni`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/backupenginejni.cc -->
