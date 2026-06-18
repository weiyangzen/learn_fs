# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TimedEnv.java

## Purpose
`TimedEnv` wraps a base `Env` with native timing instrumentation for filesystem operations, reporting timings through RocksDB `PerfContext` variables.

## Important APIs and Types
The constructor takes a base `Env` and calls native `createTimedEnv`. Disposal releases the timed environment through `disposeInternalJni`.

## Control Flow
Construction passes the base environment handle to native code. All timed filesystem behavior is implemented by the native environment wrapper.

## State and Persistence Behavior
The Java object owns the native timed environment. The base environment must remain live while the timed wrapper is in use. No filesystem data is persisted by this class itself.

## Dependencies and Integration Points
It extends `Env` and integrates with options/configuration paths that accept an environment handle. It reports to `PerfContext` rather than Java fields.

## Risks and Test Signals
Tests should cover base-env lifetime, disposal ordering, timing values appearing in `PerfContext`, and behavior with default/custom envs. The main lifecycle risk is closing the base environment too early.
