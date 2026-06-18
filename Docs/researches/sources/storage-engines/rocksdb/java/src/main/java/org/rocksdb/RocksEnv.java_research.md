# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/RocksEnv.java

## Purpose
`RocksEnv` is an `Env` wrapper for a native RocksDB environment handle. It represents operating-system services such as filesystem access and is documented as thread-safe for concurrent use.

## Important APIs and Types
- Extends `Env`.
- Package-private constructor `RocksEnv(long handle)`.
- Overrides `disposeInternal(long)` to call `disposeInternalJni(long)`.

## Control Flow
Instances are created internally when a native environment handle needs a Java wrapper, notably from `RocksDB.getEnv()` when the DB environment is not the default. The constructor passes the handle to `Env`. Disposal delegates to JNI, although callers creating wrappers for non-owned handles typically disown them.

## State and Persistence Behavior
The Java object stores the inherited native environment handle. It does not itself persist data, but the native environment controls how RocksDB accesses persistent files. The constructor documentation states ownership remains with the caller, so disposing a wrapper created for a borrowed handle should be a no-op after ownership is disowned.

## Dependencies and Integration Points
It depends on `Env` and native JNI implementation. It integrates with `RocksDB.getEnv()`, which returns `Env.getDefault()` for the default handle or a disowned `RocksEnv` for other DB environments.

## Risks
Ownership semantics are subtle. If a borrowed environment wrapper is not disowned by its creator, Java close could free an environment still owned by native DB/options code. Conversely, owned environment subclasses must still dispose correctly.

## Test Signals
Tests should cover `RocksDB.getEnv()` returning the singleton default for default DBs, returning a disowned wrapper for custom environments, and safe close behavior for borrowed handles.
