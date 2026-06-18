# sources/storage-engines/rocksdb/java/samples/src/main/java/OptimisticTransactionSample.java

## Purpose
This sample demonstrates Java `OptimisticTransactionDB` usage with read committed behavior, repeatable-read snapshot isolation, and monotonic atomic views using multiple snapshots.

## Important APIs, Types, and Functions
The class uses `Options`, `OptimisticTransactionDB`, `WriteOptions`, `ReadOptions`, `OptimisticTransactionOptions`, `Transaction`, `Snapshot`, `RocksDBException`, and `Status.Code.Busy`. Helper methods are `readCommitted`, `repeatableRead`, and `readCommitted_monotonicAtomicViews`.

## Control Flow
`main` opens an optimistic transaction DB at `/tmp/rocksdb_optimistic_transaction_example`, creates read/write options, and calls three scenario helpers. `readCommitted` starts a transaction, reads missing data, writes inside the transaction, verifies outside reads do not see it, writes another key outside, and commits. `repeatableRead` starts with `setSetSnapshot(true)`, captures the transaction snapshot, writes the same key outside, reads for update through the snapshot, expects commit conflict as `Busy`, and rolls back. The monotonic atomic view example advances snapshots during a transaction so an outside write can become visible without creating a conflict.

## State and Persistence Behavior
The sample writes to a persistent DB under `/tmp`. It mutates transaction-local write batches, DB state on commit, and read option snapshot state. `finally` blocks clear snapshots from `ReadOptions` after snapshot invalidation.

## Dependencies and Integration Points
It integrates public Java APIs with the native bridges in transaction and optimistic transaction JNI code. It is a user-facing example rather than a formal test, but it exercises snapshot and conflict semantics.

## Risks and Edge Cases
The fixed `/tmp` path can leave state between runs. Assertions require JVM assertions to be enabled to enforce checks. The monotonic view example contains `txn.put(valueX, valueX)` after reading key `x`, likely intentional or a sample typo, since it uses the value bytes as the key.

## Test Signals
The sample signals expected behavior for optimistic conflicts: outside writes to a read key should produce `Status.Code.Busy`, while unrelated outside writes should not block commit. It also signals that `ReadOptions.setSnapshot(null)` is required after transaction snapshot lifetime ends.
