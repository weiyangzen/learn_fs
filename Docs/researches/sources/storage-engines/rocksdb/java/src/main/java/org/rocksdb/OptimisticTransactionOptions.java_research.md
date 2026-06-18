# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/OptimisticTransactionOptions.java research

## Purpose

`OptimisticTransactionOptions` wraps native options for optimistic transactions. It controls whether transactions take snapshots and which comparator should be used when the DB has a non-default comparator.

## Important APIs and types

The constructor creates a native options object. It implements `TransactionalOptions<OptimisticTransactionOptions>` through `isSetSnapshot()` and `setSetSnapshot(boolean)`. `setComparator(AbstractComparator)` passes a comparator native handle for transaction write-batch indexing.

## Control flow

Each public method asserts ownership and calls a direct native getter or setter. Disposal calls `disposeInternalJni(handle)`.

## State and persistence behavior

State lives in the native options handle. Snapshot choice affects transaction read/conflict semantics. Comparator choice affects in-memory transaction indexing; persistent correctness depends on matching the DB comparator.

## Dependencies and integration points

It integrates with `OptimisticTransactionDB.beginTransaction(...)`, `Transaction`, `WriteBatchWithIndex`, and `AbstractComparator`.

## Risks and test signals

Risks include using a closed comparator or forgetting to set a non-default comparator, which can break transaction conflict/index ordering. Tests should cover getter/setter round-trips, transactions with and without snapshots, custom comparator transactions, and disposal behavior.
