# sources/storage-engines/rocksdb/utilities/transactions/transaction_base.cc

## Purpose

This file implements `TransactionBaseImpl`, the shared base for RocksDB transaction implementations, and `Transaction::CommitAndTryCreateSnapshot()`. It provides write-batch management, snapshot lifecycle, savepoints, read-your-own-write reads, lock tracking, transactional iterators, entity/multi-get APIs, untracked writes, operation counters, recovery rebuild from write batches, and commit-time snapshot request state.

## Important APIs And Functions

- `CommitAndTryCreateSnapshot()` validates or sets the commit timestamp, requests snapshot creation on commit, calls virtual `Commit()`, and returns the created timestamped snapshot.
- `Clear()` and `Reinitialize()` reset batches, locks, savepoints, counters, snapshots, ID/name/log number, write options, comparator/protection state, and indexing mode.
- Snapshot methods include `SetSnapshot`, `SetSnapshotInternal`, `SetSnapshotOnNextOperation`, and `SetSnapshotIfNeeded`.
- Savepoint methods include `SetSavePoint`, `RollbackToSavePoint`, and `PopSavePoint`.
- Read APIs include `Get`, `GetEntity`, `GetForUpdate`, `GetEntityForUpdate`, `MultiGet`, `MultiGetEntity`, and `MultiGetForUpdate`.
- Iterator APIs include `GetIterator`, `GetCoalescingIterator`, `GetAttributeGroupIterator`, and templated `NewMultiCfIterator`.
- Write APIs include put/entity/merge/delete/single-delete and untracked variants.
- Utilities include `TrackKey`, `GetBatchForWrite`, `UndoGetForUpdate`, `RebuildFromWriteBatch`, and `GetCommitTimeWriteBatch`.

## Control Flow

Reads use `WriteBatchWithIndex` overlay helpers so transaction-local writes shadow DB state. `Get` and `MultiGet` normalize `ReadOptions::io_activity`; get-for-update methods lock before reading and reject undefined validation/snapshot combinations.

Writes call virtual `TryLock()` with exclusive write intent, append to either `WriteBatchWithIndex` or the raw write batch depending on indexing mode, and increment counters. Untracked writes still lock but skip validation.

Savepoints store snapshot state, pending snapshot creation state, counters, and a per-savepoint lock tracker. Rollback restores those fields, rolls back the write batch, subtracts newly tracked locks, and pops the savepoint. Pop merges lock state downward when nested savepoints remain.

`NewMultiCfIterator()` validates non-empty CF lists and comparator compatibility, obtains DB iterators, overlays transaction-local batches, and constructs coalescing or attribute-group iterators.

`RebuildFromWriteBatch()` reconstructs a transaction from a persisted batch by stripping timestamp suffixes according to CF comparator metadata and replaying operations through public transaction write APIs; metadata markers are rejected.

## State And Persistence Behavior

The base owns runtime transaction state: DB pointer, write options, comparator, start time, write batch, commit-time batch, savepoints, counters, lock tracker, snapshot shared pointer, notifier, ID/name/log number, and indexing mode. It does not persist commits directly; concrete subclasses implement prepare/commit/rollback persistence.

Snapshots use a `shared_ptr` custom deleter that calls `DB::ReleaseSnapshot()`. `DisableIndexing()` affects read-your-own-write visibility and later timestamp-size inference by subclasses.

## Dependencies And Integration Points

The implementation depends on `DBImpl`, column-family/comparator internals, `WriteBatchWithIndex`, `LockTracker`, coalescing and attribute-group iterators, wide-column serialization, logging, and virtual lock hooks supplied by optimistic or pessimistic transaction subclasses.

## Risks And Test Signals

Risks include snapshot release lifetime, notifier timing, savepoint-aware lock untracking, indexing-disabled write behavior, partial locking in `MultiGetForUpdate`, and recovery rebuild timestamp stripping. `optimistic_transaction_test.cc` directly covers savepoints, untracked writes, entity APIs, iterators, `UndoGetForUpdate`, and operation counters; timestamped snapshot tests cover `CommitAndTryCreateSnapshot()`.
