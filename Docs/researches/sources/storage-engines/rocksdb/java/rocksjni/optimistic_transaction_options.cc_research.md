# sources/storage-engines/rocksdb/java/rocksjni/optimistic_transaction_options.cc

## Purpose
Implements the JNI bridge for Java `OptimisticTransactionOptions`, allowing Java to allocate, configure, inspect, and dispose C++ `ROCKSDB_NAMESPACE::OptimisticTransactionOptions`. These options are passed to `OptimisticTransactionDB::BeginTransaction` to control snapshot setup and comparator use for optimistic transaction conflict tracking.

## Important APIs, Types, And Functions
The exported JNI functions are `Java_org_rocksdb_OptimisticTransactionOptions_newOptimisticTransactionOptions`, `Java_org_rocksdb_OptimisticTransactionOptions_isSetSnapshot`, `Java_org_rocksdb_OptimisticTransactionOptions_setSetSnapshot`, `Java_org_rocksdb_OptimisticTransactionOptions_setComparator`, and `Java_org_rocksdb_OptimisticTransactionOptions_disposeInternalJni`. They operate on `OptimisticTransactionOptions::set_snapshot` and `OptimisticTransactionOptions::cmp`, using native handles for `OptimisticTransactionOptions` and `Comparator`.

## Control Flow
Construction allocates a default `OptimisticTransactionOptions` and returns its pointer as a Java long handle. `isSetSnapshot` casts the handle and returns the current `set_snapshot` field. `setSetSnapshot` casts the handle and writes the Java boolean into `set_snapshot`. `setComparator` casts both the options handle and comparator handle and stores the comparator pointer in `opts->cmp`. Disposal deletes the options object behind the handle.

## State And Persistence Behavior
The options object is transient configuration, not persisted DB state. `set_snapshot` affects future transactions begun with the options: RocksDB can take a transaction snapshot at begin time, enabling repeatable-read style behavior. `cmp` is a borrowed pointer to a comparator owned elsewhere; it affects key comparison inside optimistic transaction internals when a DB uses a non-default comparator. The native options object must remain alive until `BeginTransaction` has consumed it, and the comparator object must remain alive for any transaction logic that dereferences `cmp`.

## Dependencies And Integration Points
Depends on generated `org_rocksdb_OptimisticTransactionOptions.h`, `rocksdb/utilities/optimistic_transaction_db.h`, `rocksdb/comparator.h`, and pointer conversion helpers. Java integration is in `OptimisticTransactionOptions.java`, whose fluent methods call these native functions after checking `isOwningHandle()`. The options are consumed by `optimistic_transaction_db.cc` `beginTransaction` overloads. Comparator handles commonly come from `AbstractComparator` subclasses such as `BytewiseComparator`, and the Java API documents this as needed for DBs with non-default comparators.

## Risks And Edge Cases
`setComparator` stores a raw borrowed `Comparator*` without increasing lifetime ownership, so Java code must keep the comparator alive at least as long as options and any transactions needing it. There is no null-handle validation; invalid handles become undefined native behavior. Boolean conversion relies on `jboolean` mapping cleanly into the C++ bool field. Disposal is straightforward, but using an options handle after close or passing it concurrently while mutating fields from Java would be unsafe in the usual RocksJNI native-handle model.

## Test Signals
`OptimisticTransactionOptionsTest.setSnapshot` sets a random boolean and reads it back through JNI, directly covering `setSetSnapshot` and `isSetSnapshot`. `OptimisticTransactionOptionsTest.comparator` constructs a direct-buffer `BytewiseComparator` and calls `setComparator`, covering handle assignment and basic lifecycle. `OptimisticTransactionDBTest` and `OptimisticTransactionSample` exercise these options when beginning transactions, especially `setSetSnapshot(true)` for repeatable-read examples.
