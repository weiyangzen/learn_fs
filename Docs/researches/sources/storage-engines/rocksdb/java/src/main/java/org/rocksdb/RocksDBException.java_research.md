# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/RocksDBException.java

## Purpose
`RocksDBException` is the checked exception used by RocksJNI APIs to report failures from native RocksDB operations. It carries the Java exception message and, when available, the native `Status` object that explains the RocksDB error code/subcode/state.

## Important APIs and Types
- Extends `Exception`.
- Stores nullable `Status status`.
- Constructors accept a plain message, message plus `Status`, or a `Status` alone.
- `getStatus()` exposes the native status wrapper or null.

## Control Flow
Message-only construction delegates to the message/status constructor with `null`. Status-only construction derives the exception message from `status.getState()` when present, otherwise from `status.getCodeString()`, then stores the status. API callers catch `RocksDBException` from higher-level wrappers such as `RocksDB`, iterators, environments, and managers.

## State and Persistence Behavior
The class has no persistence behavior. Its only state is immutable after construction: the inherited exception message/stack trace and the stored `Status`. It does not own or close native resources.

## Dependencies and Integration Points
It depends on `org.rocksdb.Status`. It is the shared error contract for JNI methods declared across the package, allowing callers to inspect structured status when native code provided one.

## Risks
Status is annotated only by comment as nullable, so callers must check for null. The status-only constructor assumes the input status is non-null. If native bindings construct exceptions inconsistently, downstream code may see a generic message without structured status.

## Test Signals
Tests should verify message derivation from status state versus code string, null status behavior for message constructors, and that JNI paths preserve `Status` metadata when throwing.
