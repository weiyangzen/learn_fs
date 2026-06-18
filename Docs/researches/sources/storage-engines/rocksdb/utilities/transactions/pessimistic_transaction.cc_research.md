# sources/storage-engines/rocksdb/utilities/transactions/pessimistic_transaction.cc

## Purpose

This file implements pessimistic transaction mechanics and the concrete `WriteCommittedTxn` policy. It manages transaction IDs, lock acquisition/release, expiration and lock stealing, snapshot and user-timestamp validation, prepare/commit/rollback state transitions, write-batch timestamping, commit-time snapshot creation, and persistence through `DBImpl::WriteImpl()`.

## Important APIs, Types, And Functions

- `PessimisticTransaction::Initialize()` maps `TransactionOptions` into lock timeout, deadlock, expiration, snapshot, skip-prepare, skip-concurrency-control, and commit optimization state.
- `Prepare`, `Commit`, `CommitBatch`, `Rollback`, `RollbackToSavePoint`, and `SetName` implement the transaction state machine.
- `TryLock()` is the central point-lock path and handles lock upgrades, tracked locks, snapshot validation, and `assume_tracked`.
- `ValidateSnapshot()` delegates conflict checks to `TransactionUtil::CheckKeyForConflicts()`.
- `LockBatch()` extracts write-batch keys, sorts by CF/key, and locks deterministically for direct `TransactionDB::Write()` wrapping.
- `WriteCommittedTxn` overrides read-for-update and write APIs to support timestamp-aware CFs and write-committed persistence hooks.

## Control Flow

Construction initializes the shared base, stores `PessimisticTransactionDB`/`DBImpl`, and optionally calls `Initialize()`. Destruction and `Clear()` unlock all tracked locks; named in-flight transactions are unregistered unless committed.

`Prepare()` requires a transaction name, rejects expiration, transitions to `AWAITING_PREPARE`, clears expiration, writes an end-prepare marker to WAL with memtable disabled, and moves to `PREPARED`. `Commit()` either commits a prepared transaction through `CommitInternal()` or, for allowed unprepared paths, commits directly through `CommitWithoutPrepareInternal()`. Failed prepared commit marker writes restore `PREPARED` so callers can retry or roll back. `Rollback()` writes rollback markers for prepared transactions and preserves state on retryable write failures.

`TryLock()` first handles skip-concurrency-control, existing lock status, and lock upgrades. It then sets a snapshot if requested, validates against snapshot/timestamp when required, undoes a just-acquired lock on validation failure, and tracks successful locks for cleanup/savepoints.

## State And Persistence Behavior

In-memory state includes transaction ID, expiration time, lock/deadlock timeouts, waiting transaction IDs, read/commit timestamps, lock trackers, and commit optimization thresholds. Persistent state is written through prepare, commit, rollback, and data write batches.

Write-committed prepare writes WAL-only prepare markers. Commit writes commit markers and, unless bypass optimization is selected, appends prepared data into the commit-time batch so memtables contain committed data. Large commits can bypass memtable insertion only when timestamps are absent, WBWI/raw batch counts match, thresholds are met, and blob direct-write CFs are not present.

Timestamped writes require a read timestamp for validation and a commit timestamp before persistence. Commit paths update batch timestamps and can create timestamped snapshots through `SnapshotCreationCallback`.

## Dependencies And Integration Points

This implementation integrates with `PessimisticTransactionDB`, `DBImpl`, lock managers, `WriteBatchInternal`, `WriteBatchWithIndexInternal`, WAL prepare tracking, `TransactionUtil`, `SnapshotCreationCallback`, logging/stats, and `SyncPoint`.

## Risks And Test Signals

Risks include atomic state transitions around expirable lock stealing, lock upgrade rollback after validation failure, misuse of `assume_tracked`, timestamp-size inference when indexing is disabled, commit-bypass correctness, and preserving rollbackability after failed prepared commit writes. Test hooks exist for expirable commit races and bypass-memtable commits; timestamped snapshot behavior is exercised by the timestamped snapshot tests.
