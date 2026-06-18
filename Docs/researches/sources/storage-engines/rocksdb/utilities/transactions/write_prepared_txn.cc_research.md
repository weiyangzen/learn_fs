# sources/storage-engines/rocksdb/utilities/transactions/write_prepared_txn.cc

## Purpose

This file implements `WritePreparedTxn`, the per-transaction object for RocksDB's write-prepared transaction policy. In write-prepared 2PC, `Prepare()` writes user data to WAL and memtable immediately, but that data is not visible until `Commit()` writes a commit marker and the DB publishes the prepare sequence through the write-prepared commit map. This implementation adapts pessimistic transaction behavior to that policy by overriding reads, prepare, commit, rollback, snapshot validation, snapshot creation, and rebuild-from-WAL/batch behavior.

## Important APIs and functions

The constructor stores the owning `WritePreparedTxnDB*` and calls `Initialize()` after the base constructor so virtual overrides such as `SetSnapshot()` can be used correctly. `Initialize()` delegates to `PessimisticTransaction::Initialize()` and resets `prepare_batch_cnt_`.

`Get()`, `GetImpl()`, and `MultiGet()` wrap reads with `WritePreparedTxnReadCallback`. They call `wpt_db_->AssignMinMaxSeqs()` to get the read snapshot sequence and the smallest uncommitted sequence, then read through `write_batch_` plus DB. Callback validity and `wpt_db_->ValidateSnapshot()` are checked afterward; invalid unbacked snapshots return `Status::TryAgain()` and record `TXN_GET_TRY_AGAIN`.

`GetIterator()` deliberately obtains the base iterator from `WritePreparedTxnDB::NewIterator()` rather than the root DB, then overlays the transaction write batch with `NewIteratorWithBase()`. `GetCoalescingIterator()` and `GetAttributeGroupIterator()` return `NotSupported` error iterators for write-prepared/write-unprepared transactions.

`PrepareInternal()` marks the write batch with `MarkEndPrepare`, computes duplicate-key sub-batches via `SubBatchCnt()`, and writes the batch to WAL and memtable through `DBImpl::WriteImpl()`. It installs `AddPreparedCallback` as a pre-release callback so prepared sequences are added to `prepared_txns_` in sequence order before the write is released to readers. The returned sequence becomes the transaction id and prepare sequence.

`CommitInternal()` writes a commit marker and updates the commit map. For the normal case where the commit-time batch is empty, it writes WAL-only with memtable disabled and uses `WritePreparedCommitEntryPreReleaseCallback` to add commit entries and publish sequence numbers. If the commit-time batch contains data, the code only permits it for `use_only_the_last_commit_time_batch_for_recovery_`; otherwise it rejects the transaction because commit-time data can create two uncommitted versions of a key and break compaction invariants. In two-write-queue mode with commit-time data, it may perform a second empty write to the nonmem queue to publish the sequence and commit both the prepare batch and auxiliary data batch.

`CommitWithoutPrepareInternal()` and `CommitBatchInternal()` support non-2PC direct commits by computing the sub-batch count and delegating to `WritePreparedTxnDB::WriteInternal()`.

`RollbackInternal()` constructs a rollback batch that restores each written key to the value visible before the transaction, or deletes/single-deletes it if no prior value exists. It reads prior values using a max snapshot and a write-prepared read callback, adds a rollback marker, writes the rollback batch to memtable, and then commits both the original prepared sequence and rollback sequence in the commit map so snapshots and compaction can treat the canceled prepared data consistently. Two-write-queue rollback uses an extra empty WAL-only write and `WritePreparedRollbackPreReleaseCallback` to publish.

`ValidateSnapshot()` performs write-conflict validation for a tracked key by using the transaction snapshot's `min_uncommitted_`, a `WritePreparedTxnReadCallback`, and `TransactionUtil::CheckKeyForConflicts()`. `SetSnapshot()` obtains an enhanced snapshot from `WritePreparedTxnDB::GetSnapshotInternal()` so it includes `min_uncommitted_`. `RebuildFromWriteBatch()` delegates to the base class and refreshes `prepare_batch_cnt_`.

## Control flow

Read flow starts with io-activity validation, fills a read callback with `snap_seq` and `min_uncommitted`, reads from the transaction batch and DB, then checks that the callback never saw a released unbacked snapshot. For DB-backed snapshots validation is always true; for unbacked reads the snapshot sequence must still be above `max_evicted_seq_`.

Prepare flow is one write: mark end prepare, count sub-batches, install `AddPreparedCallback`, call `WriteImpl()` with memtable enabled, record `seq_used` as the transaction id. Commit flow is normally one WAL-only write: mark commit, install commit-entry callback, call `WriteImpl()` with memtable disabled, and let the callback add commit entries, publish `LastPublishedSequence`, and remove prepared state. The less common commit-time-data flow can be two writes so data insertion and sequence publishing remain correctly ordered.

Rollback flow is more complex: build compensating mutations by iterating the prepared write batch, read previous committed values with a write-prepared callback, append rollback marker, write the rollback mutations, then publish commit metadata that makes the original prepared versions invisible and the rollback batch visible. Cleanup of prepared entries is carefully delayed until after publishing in paths where `SmallestUnCommittedSeq()` depends on the ordering.

## State and persistence behavior

`prepare_batch_cnt_` is the key per-transaction state added by this class. It records how many sequence-number slots the prepared batch occupies when duplicate keys require multiple sub-batches. The value is used by commit and rollback callbacks to add or remove all relevant prepare sequences from the DB's prepared structures.

Prepare data is durable because `PrepareInternal()` forces WAL enabled. Commit markers are durable WAL records but usually do not touch memtables. Rollback writes compensating data and a rollback marker. The transaction id is set to the prepare sequence and later used as the primary key into commit metadata and recovered transaction lookup.

## Dependencies and integration points

This file depends on `DBImpl::WriteImpl`, `WriteBatchInternal` marker helpers, `WriteBatchWithIndex` read-overlay methods, `WritePreparedTxnDB` visibility helpers, pre-release callbacks declared in `write_prepared_txn_db.h`, `TransactionUtil::CheckKeyForConflicts`, and pessimistic transaction base behavior. It integrates with two-write-queue publishing through `DBImpl::immutable_db_options().two_write_queues`, `SetLastPublishedSequence`, and memtable-disabled WAL-only writes.

## Risks

The largest risks are ordering bugs around pre-release callbacks. `AddPrepared` must happen before readers can see a prepared sequence; `AddCommitted` and `SetLastPublishedSequence` must happen before a commit is visible; `RemovePrepared` must happen after publishing or `SmallestUnCommittedSeq()` can move too far forward. Commit-time batches are risky enough that this file rejects them unless the recovery-only option is enabled. Rollback is also sensitive because it synthesizes user mutations from old values and must avoid double-processing duplicate keys.

## Test signals

Coverage comes mainly from `write_prepared_transaction_test.cc`: prepare/commit/recovery in `BasicRecovery`, rollback in `Rollback` and `RollbackPreparedAfterCommitWriteFailure`, duplicate-key sub-batch behavior in `WriteBatchWithIndex.SubBatchCnt` and `AdvanceMaxEvictedSeqWithDuplicates`, commit-time sequence ordering in `SeqAdvanceConcurrent`, visibility reads in `IsInSnapshot` and `Iterate`, compaction interaction in the compaction tests, and two-write-queue races in `AddPreparedBeforeMax` and `CommitOfDelayedPrepared`.
