# sources/storage-engines/rocksdb/include/rocksdb/utilities/transaction.h

## Purpose
Core transaction interface shared by optimistic and pessimistic transaction DBs, covering snapshots, reads, tracked writes, savepoints, 2PC, conflict tracking, and transaction state.

## Important APIs, Types, And Functions
Defines `TransactionName`, `TransactionID`, `TxnTimestamp`, `Endpoint`, `TransactionNotifier`, and abstract `Transaction`. Major methods include snapshot APIs, `Prepare`, `Commit`, `CommitAndTryCreateSnapshot`, `Rollback`, savepoints, `Get`, `GetForUpdate`, range locks, transactional iterators, tracked/untracked mutations, indexing control, counters, write-batch access, lock/deadlock timeouts, `UndoGetForUpdate`, commit-time batch, names/ids, wait-for inspection, state, and timestamp APIs.

## Control Flow, State, And Persistence
Transactions collect operations in an indexed write batch. Reads can see pending writes; `GetForUpdate` also tracks or locks keys. Snapshots establish validation points. `Prepare` persists 2PC intent where supported, `Commit` validates and writes atomically, and `Rollback` discards or writes rollback records. Local state includes log number, name, atomic state, id, snapshots, tracked keys, and write batches.

## Dependencies And Integration Points
Depends on `DB`, `Comparator`, `Iterator`, `WriteBatchWithIndex`, `Status`, snapshots, wide-column APIs, and transaction DB implementations. Integrates with WAL recovery, 2PC, user-defined timestamps, and secondary index maintenance.

## Risks And Edge Cases
Caller must synchronize access to a transaction. Prepared transactions may need explicit resolution after commit errors. Rollback can return retryable I/O errors. Disabling indexing makes later reads of those pending keys undefined. Direct mutation of `GetWriteBatch()` can bypass transaction metadata. Commit-time batches bypass concurrency control.

## Test Signals
Cover snapshot conflicts, deferred snapshot notifier, 2PC recovery, rollback errors, savepoints, read-your-own-writes, merge-in-progress, locks/conflicts, untracked writes, disabled indexing, commit-time batch restrictions, state transitions, timestamps, and range locks.
