# sources/storage-engines/rocksdb/utilities/transactions/pessimistic_transaction.h

## Purpose

This header declares `PessimisticTransaction`, the shared pessimistic concurrency-control transaction base, and `WriteCommittedTxn`, the concrete write-committed transaction implementation. It defines transaction lifecycle, locking, timeout/deadlock observability, expiration, naming, timestamp validation, and abstract persistence hooks.

## Important APIs, Types, And Members

`PessimisticTransaction` derives from `TransactionBaseImpl` and exposes `Prepare`, `Commit`, `CommitBatch`, `Rollback`, `RollbackToSavePoint`, `SetName`, `GetID`, waiting-transaction diagnostics, lock/deadlock timeout setters, expiration queries, `TryStealingLocks`, range locks, and `CollapseKey`.

Protected hooks split common locking from policy-specific persistence: `PrepareInternal`, `CommitWithoutPrepareInternal`, `CommitBatchInternal`, `CommitInternal`, and `RollbackInternal`. Protected helpers include `LockBatch`, `TryLock`, `ValidateSnapshot`, and `UnlockGetForUpdate`.

Key state includes `txn_db_impl_`, `db_impl_`, `expiration_time_`, `read_timestamp_`, `commit_timestamp_`, transaction ID, waiting key/CF metadata, lock timeouts, deadlock flags, skip-concurrency-control flag, skip-prepare flag, and commit-bypass thresholds.

`WriteCommittedTxn` overrides get-for-update, entity get-for-update, put/entity/delete/single-delete/merge and untracked variants, commit timestamp APIs, and persistence hooks. It tracks timestamp-enabled CF IDs written while indexing is disabled.

## Control Flow And Design

The header makes `PessimisticTransaction` responsible for concurrency control and state transitions while letting subclasses choose persistence format. This supports write-committed, write-prepared, and write-unprepared policies sharing the same lock/validation machinery.

Waiting transaction state is guarded by `wait_mutex_`. `waiting_key_` is borrowed only while lock-manager wait code owns the key object, while `timed_out_key_` owns a stable copy after timeout.

## State And Persistence Behavior

The declared state is mostly runtime-only. Durable effects are delegated to subclass hooks that write prepare/commit/rollback markers or data batches through `DBImpl`. `read_timestamp_` and `commit_timestamp_` use `kMaxTxnTimestamp` as the unset sentinel.

## Dependencies And Integration Points

The header connects public transaction APIs, snapshots, write batches, DB write callbacks, autovectors, `TransactionBaseImpl`, and `TransactionUtil`. It forward-declares `PessimisticTransactionDB` and uses friend tests for snapshot validation.

## Risks And Test Signals

Risks include waiting-key lifetime, object-address transaction IDs under range locking, millisecond-to-microsecond timeout conversion, timestamp support being limited to write-committed transactions, and unsafe use of skip-concurrency-control. The API is exercised by the wider transaction suite; this subset covers shared base APIs and timestamped snapshot behavior.
