# sources/storage-engines/rocksdb/java/rocksjni/transaction_notifier.cc

## Purpose
This file creates and disposes native callback wrappers for Java `AbstractTransactionNotifier`. It lets Java code provide a transaction notifier used when a transaction snapshot is created on the next operation.

## Important APIs, Types, and Functions
The file exports `createNewTransactionNotifier` and `disposeInternalJni`. Creation allocates a `TransactionNotifierJniCallback`, wraps it in a `std::shared_ptr`, and returns a pointer to that shared pointer.

## Control Flow
Creation receives the Java callback object, constructs the C++ callback with the current `JNIEnv`, then allocates a shared pointer wrapper. Disposal casts the handle back to `std::shared_ptr<TransactionNotifierJniCallback>*` and deletes the wrapper, decrementing the reference count.

## State and Persistence Behavior
The native state is callback ownership and lifetime only. No RocksDB data is persisted. The shared pointer is passed to transaction code through `transaction.cc` when Java calls `setSnapshotOnNextOperation`.

## Dependencies and Integration Points
It depends on `TransactionNotifierJniCallback`, pointer conversion helpers, and the generated Java notifier header. It integrates with Java `AbstractTransactionNotifier` and C++ `Transaction::SetSnapshotOnNextOperation`.

## Risks and Edge Cases
Ownership is nontrivial because Java stores a pointer to a shared pointer, not the callback object itself. Disposing while a transaction still holds a shared reference is safe at the C++ object level, but disposing too early must not leave Java-side assumptions inconsistent. The TODO notes possible future refactoring around callback ownership.

## Test Signals
Tests should verify notifier creation, callback invocation when snapshots are created, and disposal after use. Lifetime tests should include a notifier passed to a transaction and disposed after the transaction no longer needs it.
