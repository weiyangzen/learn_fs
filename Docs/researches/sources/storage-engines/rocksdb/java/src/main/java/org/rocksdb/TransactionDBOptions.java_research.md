# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TransactionDBOptions.java

## Purpose
`TransactionDBOptions` is the Java JNI wrapper for native transaction database configuration. It extends `RocksObject`, owns a native `TransactionDBOptions` handle, and exposes lock-table and write-policy settings used when opening/configuring `TransactionDB`.

## Important APIs and Types
The public API is a fluent getter/setter surface: `get/setMaxNumLocks`, `get/setNumStripes`, `get/setTransactionLockTimeout`, `get/setDefaultLockTimeout`, and `get/setWritePolicy`. `setWritePolicy` maps `TxnDBWritePolicy` enum values to native bytes, while `getWritePolicy` maps the native byte back through `TxnDBWritePolicy.getTxnDBWritePolicy`.

## Control Flow, State, and Persistence
Construction calls `newTransactionDBOptions()` and stores the returned native pointer. Every accessor asserts `isOwningHandle()` before dispatching to JNI. The Java object itself persists no option values; all state lives in the native handle until `disposeInternal` calls `disposeInternalJni`. Lock timeout semantics are important: zero means no wait, negative can mean no timeout or fallback depending on setting, and comments warn about deadlocks when no timeout is used.

## Dependencies and Integration Points
This class depends on `RocksObject`, `TxnDBWritePolicy`, `TransactionOptions`, and native JNI implementations. It integrates with transaction DB open paths and external direct writes through default lock timeout behavior. The commented custom mutex factory block indicates unsupported or deferred Java binding for native transaction mutex customization.

## Risks and Test Signals
Risks concentrate around native lifetime, assertion-only disposed-handle checks, and invalid enum byte values from JNI producing `IllegalArgumentException`. Deadlock risk is explicitly documented for negative lock timeouts. In this subset, `AbstractTransactionTest` exercises transaction behavior broadly but does not directly validate these option getters/setters; coverage likely lives in transaction-specific tests outside this item.
