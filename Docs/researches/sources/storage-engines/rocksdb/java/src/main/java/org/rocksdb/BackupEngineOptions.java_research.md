# Research: sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/BackupEngineOptions.java

- **Purpose:** Java wrapper for native backup engine configuration.
- **Important APIs/types/functions:** Constructor validates a writable directory and calls `newBackupEngineOptions`. Options include backup directory, backup `Env`, shared table files, info log, sync, destroy old data, log-file backup, numeric backup/restore rate limits, rate limiter objects, checksum-based sharing, max background operations, and callback trigger interval.
- **Control flow:** Construction rejects null/non-directory/non-writable paths. Fluent setters assert ownership, call JNI setters, and retain Java references for objects that native code uses (`Env`, `Logger`, `RateLimiter`) to prevent premature GC/close. Rate limit setters normalize non-positive values to zero.
- **State and persistence behavior:** Native options persist backup behavior. Java fields retain referenced native wrappers; scalar getters read from native state except retained-object getters return Java references.
- **Dependencies:** Depends on `File`, `Env`, `Logger`, `RateLimiter`, `BackupEngine`, `RocksObject`, and JNI option functions.
- **Integration points:** Passed to `BackupEngine.open`; controls filesystem I/O, rate limiting, shared-file semantics, logging, and callback cadence for backup/restore operations.
- **Risks:** Constructor requires directory to already exist and be writable. Passing null to object setters is not handled. Java-retained object references must outlive the options/engine. `destroyOldData` and shared-file settings can delete or reuse backup data in ways that require careful tests.
- **Test signals:** Path validation, scalar setter/getter round-trips, retained object getters, non-positive rate limit normalization, backup engine behavior under sync/share/log-file settings, and disposal.
