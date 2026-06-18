# sources/storage-engines/rocksdb/java/rocksjni/transaction_options.cc

## Purpose
This file exposes C++ `TransactionOptions` to Java `TransactionOptions`. It configures per-transaction behavior such as snapshot creation, deadlock detection, lock timeout, expiration, deadlock depth, and maximum write batch size.

## Important APIs, Types, and Functions
Exports include `newTransactionOptions`, `isSetSnapshot`, `setSetSnapshot`, `isDeadlockDetect`, `setDeadlockDetect`, `getLockTimeout`, `setLockTimeout`, `getExpiration`, `setExpiration`, `getDeadlockDetectDepth`, `setDeadlockDetectDepth`, `getMaxWriteBatchSize`, `setMaxWriteBatchSize`, and `disposeInternalJni`.

## Control Flow
Construction allocates `TransactionOptions`. Getters cast the native handle and return raw C++ fields. Setters cast and assign raw fields. Disposal deletes the native options object.

## State and Persistence Behavior
The file mutates only an in-memory options object. These fields affect future `BeginTransaction` calls but are not persisted directly. Ownership is tied to the Java wrapper.

## Dependencies and Integration Points
It depends on the generated `org_rocksdb_TransactionOptions` JNI header, RocksDB transaction DB utilities, and pointer conversion helpers. It integrates with Java `TransactionOptions`, `TransactionDB.beginTransaction`, and optimistic transaction option analogs in the broader RocksJava API.

## Risks and Edge Cases
JNI does no validation for negative or overly large timeouts, expiration values, deadlock depth, or max write batch size. Boolean assignments rely on `jboolean` conversion to C++ `bool`. Java and native ownership must prevent use after disposal.

## Test Signals
Tests should verify option round-trips, transaction creation with `set_snapshot`, lock timeout behavior, deadlock detection toggles, expiration effects, and disposal through try-with-resources.
