# sources/storage-engines/rocksdb/java/rocksjni/transaction_notifier_jnicallback.cc

## Purpose
This file implements the C++ callback class that forwards RocksDB `TransactionNotifier::SnapshotCreated` events into Java.

## Important APIs, Types, and Functions
It defines `TransactionNotifierJniCallback::TransactionNotifierJniCallback` and `SnapshotCreated`. The constructor caches the Java `snapshotCreated` method ID using `AbstractTransactionNotifierJni`. `SnapshotCreated` calls the Java callback with the native snapshot pointer.

## Control Flow
When RocksDB invokes `SnapshotCreated`, the callback attaches or retrieves a `JNIEnv` through `getJniEnv`, calls the cached Java method on the global callback object, passes `GET_CPLUSPLUS_POINTER(newSnapshot)`, describes any Java exception to stderr, and releases the JNI environment if it attached the current thread.

## State and Persistence Behavior
The callback stores only a method ID and the inherited global Java callback reference. It does not own the snapshot and does not persist data. The snapshot pointer is passed into Java for wrapper construction or notification use.

## Dependencies and Integration Points
It depends on `transaction_notifier_jnicallback.h`, `cplusplus_to_java_convert.h`, and `portal.h`. It is allocated by `transaction_notifier.cc` and passed through `transaction.cc` into transaction snapshot-on-next-operation flow.

## Risks and Edge Cases
The constructor does not explicitly handle a null method ID beyond storing it; later callback invocation would fail if method lookup threw. `SnapshotCreated` asserts that a JNI environment is available, so callback execution from unexpected threads relies on `JniCallback` attach support. Java exceptions are described but not propagated back into RocksDB transaction control flow.

## Test Signals
Tests should subclass `AbstractTransactionNotifier`, trigger snapshot creation, verify the Java method receives a valid snapshot handle, and exercise exception behavior in the Java callback to ensure it does not crash native code.
