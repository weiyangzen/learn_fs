<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/restorejni.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/restorejni.cc

Purpose: Bridges Java `RestoreOptions` to C++ `ROCKSDB_NAMESPACE::RestoreOptions` for backup engine restore calls.

Important APIs/types/functions: `Java_org_rocksdb_RestoreOptions_newRestoreOptions` allocates `RestoreOptions(keep_log_files)`. `Java_org_rocksdb_RestoreOptions_disposeInternalJni` asserts the handle and deletes it.

Control flow: Java passes the `keep_log_files` boolean to construction, then passes the returned native handle to backup/restore APIs. Disposal simply reinterprets the handle and deletes it.

State and persistence behavior: The object stores restore behavior only; it does not perform restore or write state itself. The option affects whether WAL/log files survive restore operations in backup engine code.

Dependencies and integration points: Includes generated `org_rocksdb_RestoreOptions.h`, `rocksdb/utilities/backup_engine.h`, and RocksJNI pointer helpers. It integrates with Java backup engine bindings that consume a `RestoreOptions` pointer.

Risks: `assert(ropt)` disappears in release builds, so invalid handles can still crash. The bridge exposes only the constructor boolean visible in this source; any future C++ fields require matching JNI additions.

Test signals: Restore tests should instantiate both `keep_log_files` modes, pass them through backup engine restore, and verify native dispose under leak sanitizers.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/restorejni.cc -->
