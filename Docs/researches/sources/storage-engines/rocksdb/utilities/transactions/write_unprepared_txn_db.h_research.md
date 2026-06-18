# sources/storage-engines/rocksdb/utilities/transactions/write_unprepared_txn_db.h

## Purpose

`write_unprepared_txn_db.h` declares the write-unprepared transaction DB wrapper and the commit pre-release callback specialized for a transaction that may have many unprepared sequence ranges. It is the public class boundary between transaction objects and the write-prepared visibility engine.

## Important APIs, types, and functions

`WriteUnpreparedTxnDB : public WritePreparedTxnDB` inherits constructors and overrides `Initialize` and `BeginTransaction`. It declares `NewIterator(ReadOptions, ColumnFamilyHandle*, WriteUnpreparedTxn*)`, a transaction-aware iterator factory distinct from normal DB iterator creation. It also declares private `RollbackRecoveredTransaction` for direct recovery cleanup.

`WriteUnpreparedCommitEntryPreReleaseCallback : public PreReleaseCallback` accepts a `WritePreparedTxnDB`, `DBImpl`, reference to `unprep_seqs`, optional commit data batch count, and `publish_seq` flag. Its `Callback` computes the last commit sequence, calls `AddCommitted` for every sequence covered by every unprepared range, optionally adds commit metadata for data written with the commit/rollback batch, and publishes the sequence in two-write-queue mode when configured.

## Control flow and state behavior

The DB class itself stores no new data members in the header; it reuses write-prepared state and implements write-unprepared behavior in the `.cc` file. The callback is stateful and must outlive the corresponding `WriteImpl` callback execution. Its `unprep_seqs_` reference points to transaction-owned sequence metadata, so callers must not clear or mutate that map until `WriteImpl` has finished invoking the callback. For each `(prepare_seq, batch_cnt)` pair, the callback commits every sequence from `prepare_seq` through `prepare_seq + batch_cnt - 1` to the same `last_commit_seq`.

If `data_batch_cnt_ > 0`, commit-time or rollback data written in the same write is also committed to the same last commit sequence. In two-write-queue mode, `SetLastPublishedSequence(last_commit_seq)` is called only when `publish_seq_` is true; some two-phase flows use a first callback to add prepared entries without publishing and a second disabled-memtable write to publish commit metadata.

## Dependencies and integration points

This header includes `write_prepared_txn_db.h` and `write_unprepared_txn.h`, and it integrates with `DBImpl`, `PreReleaseCallback`, `SequenceNumber`, and transaction internals. `WriteUnpreparedTxn` uses this callback in commit and rollback paths to update write-prepared commit-cache metadata for all unprepared batches as a unit.

## Risks and edge cases

The callback assumes `unprep_seqs` is non-empty and asserts that in the constructor. It relies on correct sub-batch counts; undercounting leaves unprepared sequence numbers uncommitted, while overcounting can incorrectly mark unrelated sequences committed. The reference member is efficient but lifetime-sensitive. Publishing in two-write-queue mode is explicitly optional, so callers must choose the flag correctly or readers may see inconsistent publication order.

## Test signals

The callback is exercised indirectly by commit and rollback tests for unprepared batches, recovery tests, and WAL prep-section tests. Two-write-queue parameterization in the test suite is important because it validates the publication branch.
