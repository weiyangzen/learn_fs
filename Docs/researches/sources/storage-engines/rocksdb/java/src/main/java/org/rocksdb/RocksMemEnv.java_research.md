# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/RocksMemEnv.java

## Purpose
`RocksMemEnv` is an in-memory `Env` implementation. It stores file data in memory while delegating non-file-storage tasks to a supplied base environment.

## Important APIs and Types
- Extends `Env`.
- Public constructor `RocksMemEnv(Env baseEnv)`.
- Native factory `createMemEnv(long baseEnvHandle)`.
- Overrides disposal through `disposeInternalJni(long)`.

## Control Flow
Construction reads `baseEnv.nativeHandle_` and passes the returned native mem-env handle to `Env`. When closed, disposal delegates to JNI. The base environment must remain alive while the mem-env is in use.

## State and Persistence Behavior
The native mem-env handle owns an in-memory filesystem. Data stored through this environment is volatile and process-local unless native implementation provides otherwise. Since it delegates non-storage tasks, behavior also depends on the base environment lifetime and configuration.

## Dependencies and Integration Points
It depends on `Env` and native RocksDB mem-env support. It can be used through DB/options environment settings to run RocksDB on an in-memory file abstraction.

## Risks
The constructor directly accesses the base native handle and does not retain an explicit Java reference, so callers must keep `baseEnv` live. Closing the base environment too early can invalidate the native mem-env. The TODO indicates naming may be legacy.

## Test Signals
Tests should validate DB creation on `RocksMemEnv`, absence of durable files, cleanup on close, base-env lifetime behavior, and error handling when the base environment is invalid.
