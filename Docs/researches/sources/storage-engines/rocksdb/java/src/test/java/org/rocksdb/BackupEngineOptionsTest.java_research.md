# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/BackupEngineOptionsTest.java

## Purpose
`BackupEngineOptionsTest` verifies Java getter/setter bindings and disposed-handle assertions for `BackupEngineOptions`.

## Important APIs and Types
Tests cover `backupDir`, `backupEnv`, `shareTableFiles`, `infoLog`, `sync`, `destroyOldData`, `backupLogFiles`, `backupRateLimit`, `backupRateLimiter`, `restoreRateLimit`, `restoreRateLimiter`, `shareFilesWithChecksum`, `maxBackgroundOperations`, and `callbackTriggerIntervalSize`.

## Control Flow, State, and Persistence
Each option test constructs `BackupEngineOptions` in try-with-resources, mutates native-backed state, and asserts the getter value. Negative backup/restore rate limits are expected to map to zero. Disposed-handle tests close the options object, set `ExpectedException` to `AssertionError`, then invoke methods on the closed object.

## Dependencies and Integration Points
Depends on `RocksNativeLibraryResource`, AssertJ, JUnit `ExpectedException`, `RocksMemEnv`, `Env`, `Logger`, `RateLimiter`, and `PlatformRandomHelper`. It validates backup option integration with envs, loggers, and rate limiters.

## Risks and Test Signals
The test gives strong binding coverage for options but relies on Java assertions being enabled for disposed-handle failures. It also confirms constructor validation rejects null backup directories. It does not create real backups; `BackupEngineTest` covers operational behavior.
