<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/backup_engine_options.cc -->
# Research: sources/storage-engines/rocksdb/java/rocksjni/backup_engine_options.cc

Purpose: Implements JNI bindings for Java `BackupEngineOptions`, exposing construction, getters, setters, and native disposal for C++ `ROCKSDB_NAMESPACE::BackupEngineOptions`.

Important APIs/types/functions: Native methods include `newBackupEngineOptions`, `backupDir`, setters/getters for `backup_env`, `share_table_files`, `info_log`, `sync`, `destroy_old_data`, `backup_log_files`, `backup_rate_limit`, backup/restore `RateLimiter`, `restore_rate_limit`, `share_files_with_checksum`, `max_background_operations`, `callback_trigger_interval_size`, and `disposeInternalJni`.

Control flow: JNI functions reinterpret Java long handles as C++ pointers, copy Java strings where needed, mutate fields on `BackupEngineOptions`, and return primitive values or new Java strings. Construction allocates with `new`; disposal deletes the native object.

State and persistence behavior: Native state lives behind the Java object's long handle. Options influence later backup/restore persistence behavior: directory, file sharing/checksum policy, log backup, sync, rate limits, background work, and old-data destruction. The options object itself is not persisted.

Dependencies and integration points: Depends on generated JNI headers, `rocksdb/utilities/backup_engine.h`, JNI conversion helpers, `portal.h`, `Env`, `RateLimiter`, and logger callback types. It is used by Java `BackupEngineOptions`.

Risks and edge cases: `setInfoLog` appears to reinterpret `jhandle` rather than the logger handle, which is a suspicious ownership/pointer bug. Raw pointer fields such as `backup_env` require Java-side lifetime discipline. String allocation failure returns early as JNI exception state.

Test signals: `BackupEngineOptionsTest` should verify each setter/getter, native disposal, rate limiter/logger behavior, and backup/restore integration. ASAN/JNI checks are useful for handle misuse.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/backup_engine_options.cc -->
