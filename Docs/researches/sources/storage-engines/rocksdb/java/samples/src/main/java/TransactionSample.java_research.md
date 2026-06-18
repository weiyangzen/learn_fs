# sources/storage-engines/rocksdb/java/samples/src/main/java/TransactionSample.java

## Purpose
This sample demonstrates `TransactionDB` usage with read committed transactions, snapshot isolation, `getForUpdate` conflict detection, savepoints, rollback, and commit.

## Important APIs, Types, and Functions
The class uses `Options`, `TransactionDBOptions`, `TransactionDB`, `WriteOptions`, `ReadOptions`, `TransactionOptions`, `Transaction`, `Snapshot`, `RocksDBException`, and `Status.Code.Busy`. Scenario helpers are `readCommitted`, `repeatableRead`, and `readCommitted_monotonicAtomicViews`.

## Control Flow
`main` opens a transaction DB under `/tmp/rocksdb_transaction_example`, creates read/write options, and runs three scenarios. `readCommitted` writes inside a transaction, verifies outside reads do not see the uncommitted write, writes another key outside, and commits. `repeatableRead` starts with a transaction snapshot, writes the same key outside, sets the snapshot on `ReadOptions`, expects `getForUpdate` to throw `Busy`, and rolls back. The monotonic view scenario advances snapshots, uses a savepoint, reads for update after an outside write, writes the key, rolls back to the savepoint, then commits.

## State and Persistence Behavior
The sample writes persistent DB state under a fixed `/tmp` path and mutates transaction-local state, locks, savepoints, snapshots, and `ReadOptions`. It clears the snapshot from read options in finally blocks.

## Dependencies and Integration Points
It exercises Java transaction APIs backed by `transaction.cc`, `transaction_db.cc`, `transaction_options.cc`, and `transaction_db_options.cc`.

## Risks and Edge Cases
Fixed DB path can retain state across runs. Assertions need JVM assertion enablement. Snapshot lifetime must be respected by clearing `ReadOptions`. The scenario intentionally uses `Status.Code.Busy` as the conflict signal.

## Test Signals
The sample gives concrete expected behavior for transaction conflict detection, rollback, savepoint rollback, snapshot advancement, and commit visibility. It is a useful smoke test for JNI transaction and transaction option bridges.
