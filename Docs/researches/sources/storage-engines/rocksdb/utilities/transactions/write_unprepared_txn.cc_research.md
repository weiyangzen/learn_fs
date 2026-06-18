# sources/storage-engines/rocksdb/utilities/transactions/write_unprepared_txn.cc

## Purpose

`write_unprepared_txn.cc` implements `WriteUnpreparedTxn`, the transaction object for RocksDB's write-unprepared policy. Unlike standard write-prepared transactions, it may flush a transaction's data to the DB before prepare, keeps a map of its own unprepared sequence ranges, lets the transaction read those ranges, and repairs state through commit, rollback, savepoint, and recovery paths.

## Important APIs, types, and functions

`WriteUnpreparedTxnReadCallback::IsVisibleFullCheck` treats any sequence in the transaction's `unprep_seqs_` ranges as visible to itself, otherwise delegates to `WritePreparedTxnDB::IsInSnapshot`. The constructor and `Initialize` configure `write_batch_flush_threshold_`, clear `unprep_seqs_`, savepoint state, active iterators, recovery flags, and untracked keys.

Write operation overrides (`Put`, `Merge`, `Delete`, `SingleDelete`) route through `HandleWrite`, which may call `MaybeFlushWriteBatchToDB` before appending and updates `largest_validated_seq_` after successful writes. `RebuildFromWriteBatch` reconstructs tracked keys during recovery without reacquiring locks. `FlushWriteBatchToDB`, `FlushWriteBatchToDBInternal`, and `FlushWriteBatchWithSavePointToDB` turn in-memory write batches into unprepared or prepared DB writes and populate `unprep_seqs_`. `PrepareInternal`, `CommitWithoutPrepareInternal`, `CommitInternal`, `RollbackInternal`, savepoint methods, `Get`, `MultiGet`, `GetIterator`, and `ValidateSnapshot` implement the external transaction behavior.

## Control flow and state behavior

Before each write, `HandleWrite` flushes the existing batch if the flush threshold is exceeded and there are no active transaction iterators. Active iterators deliberately suppress flushing because `WriteBatchWithIndex` delta iterators could point into invalid memory after a flush. `FlushWriteBatchToDBInternal` requires a transaction name, records untracked keys from the current batch, appends an end-prepare marker that can mark the batch as unprepared, counts sub-batches, and calls `DBImpl::WriteImpl` with an `AddPreparedCallback`. On success it sets the transaction ID from the first prepare sequence if needed and records `unprep_seqs_[prepare_seq] = prepare_batch_cnt_`. Unprepared flushes clear the working batch; prepared flushes retain prepare state.

Savepoint-aware flushing splits the existing write batch at recorded byte boundaries. For each segment it rebuilds a new `WriteBatchWithIndex`, flushes it as unprepared, and records a `SavePoint` containing the then-current `unprep_seqs_` plus a managed DB snapshot. Rolling back to a flushed savepoint reads the keys modified since that savepoint at the saved snapshot, builds restorative writes via `WriteRollbackKeys`, flushes them as unprepared, and then reconciles the base transaction savepoint stack with a fake in-memory savepoint.

`CommitInternal` appends a commit marker to the commit-time batch. Empty commit-time batches can update commit metadata in one disabled-memtable write. Non-empty commit-time batches are only accepted for recovery-state optimization unless the code path is changed; if data is included, duplicate-key sub-batches are counted. Two-write-queue mode may require a first write that adds prepared entries for commit-batch data followed by an empty disabled-memtable write that updates the commit map and publishes the sequence. Successful commits remove all prepared ranges from `WritePreparedTxnDB` and clear `unprep_seqs_` and savepoints.

`RollbackInternal` builds a rollback batch by reading the previous visible version of every tracked and untracked key. It writes a rollback marker, writes the restorative batch, and uses `WriteUnpreparedCommitEntryPreReleaseCallback` so the original unprepared ranges are considered committed to the rollback sequence. This lets existing commit-cache machinery make older snapshots skip canceled unprepared values. Two-write-queue rollback mirrors commit by using a second empty write to publish commit metadata. `Clear` unlocks locks unless the transaction was recovered, invalidates active iterators, clears unprepared state, and then clears base state.

Reads (`GetImpl`, `MultiGet`) call `AssignMinMaxSeqs`, use `WriteUnpreparedTxnReadCallback` with the current `unprep_seqs_`, and return `TryAgain` if an unbacked snapshot became invalid. `GetIterator` asks `WriteUnpreparedTxnDB::NewIterator` for a DB iterator widened to the transaction's max visible sequence, wraps it with `WriteBatchWithIndex`, stores it in `active_iterators_`, and registers cleanup. `ValidateSnapshot` checks conflicts with a callback that treats own unprepared ranges as visible.

## Dependencies and integration points

This implementation depends on `DBImpl::WriteImpl`, `WriteBatchInternal` markers (`MarkEndPrepare`, `MarkCommit`, `MarkRollback`, `InsertNoop`), `WriteBatchWithIndex`, `LockTracker`, `TransactionUtil::CheckKeyForConflicts`, write-prepared callbacks and commit-cache APIs, `ManagedSnapshot`, and transaction DB options such as `rollback_merge_operands`, `default_write_batch_flush_threshold`, and two-write-queue configuration. It is tightly coupled to `WriteUnpreparedTxnDB` for iterator creation, snapshot assignment, column-family handle maps, and rollback deletion policy.

## Risks and edge cases

The implementation is sequence-number sensitive. Missing a range in `unprep_seqs_`, removing prepared state before sequence publication, or using an invalid unbacked snapshot can expose uncommitted data or hide committed data. Active iterator suppression of flushing protects memory safety but can increase memory retained in the current write batch. Untracked writes are supported by scanning batches and storing keys, but the header notes they complicate snapshot validation and savepoint rollback is currently less efficient because untracked keys are not recorded per savepoint. Rollback writes all restorative keys in one batch and has TODOs for subdivision and IO priority plumbing. Recovery transactions do not hold locks and rely on `recovered_txn_` cleanup behavior.

## Test signals

`write_unprepared_transaction_test.cc` directly exercises most paths: threshold flushing, read-your-own-write, recovery reconstruction and rollback, commit/rollback after prepare, savepoint flush/rollback, untracked-key rollback, iterator invalidation, writing while iterating, and range-tombstone discard behavior under widened visible sequence numbers. Assertions on `GetUnpreparedSequenceNumbers()` check when flushes populate `unprep_seqs_`.
