# sources/storage-engines/rocksdb/java/rocksjni/transaction_notifier_jnicallback.h

## Purpose
This header declares the JNI callback adapter that implements RocksDB `TransactionNotifier` using a Java callback object.

## Important APIs, Types, and Functions
`TransactionNotifierJniCallback` inherits from `JniCallback` and `TransactionNotifier`. It declares a constructor accepting `JNIEnv*` and a Java notifier object, and overrides `SnapshotCreated(const Snapshot*)`. The private state is `jmethodID m_jsnapshot_created_methodID`.

## Control Flow
The header establishes the cross-language callback contract. RocksDB calls `SnapshotCreated`; the implementation must attach to the JVM, call Java, and release thread attachment state.

## State and Persistence Behavior
The class stores callback identity through `JniCallback` and the cached Java method ID. It does not store or own snapshots and has no persistent database behavior.

## Dependencies and Integration Points
It includes RocksDB transaction utilities and the RocksJNI `jnicallback.h` base. It is used by `transaction_notifier.cc`, `transaction_notifier_jnicallback.cc`, and `transaction.cc` snapshot notifier paths.

## Risks and Edge Cases
The header comment explicitly notes that snapshot Java object allocation is not optimized or cached, so high-frequency snapshot notifications may allocate heavily. As with all callback adapters, Java callback lifetime and native callback lifetime must remain aligned.

## Test Signals
Compile-time tests should catch signature drift against RocksDB `TransactionNotifier`. Runtime tests should validate notifier subclassing, method dispatch, snapshot handle validity, and cleanup after callback disposal.
