# sources/storage-engines/rocksdb/utilities/transactions/write_unprepared_txn.h

## Purpose

`write_unprepared_txn.h` declares the write-unprepared transaction class and its read callback. It explains the design problem: a transaction's uncommitted writes may already be in the DB, so reading its own writes cannot rely only on the in-memory `WriteBatchWithIndex`. The transaction must widen reads to the maximum of the snapshot sequence and its own unprepared sequence range, then use a custom callback to distinguish own writes, other unprepared writes, committed post-snapshot writes, and committed snapshot-visible writes.

## Important APIs, types, and functions

`WriteUnpreparedTxnReadCallback : public ReadCallback` accepts a `WritePreparedTxnDB`, snapshot sequence, `min_uncommitted`, a reference to `unprep_seqs`, and snapshot-backing mode. It overrides `IsVisibleFullCheck`, `Refresh`, and exposes `valid()`. `CalcMaxVisibleSeq` computes the read ceiling from the last unprepared range and snapshot sequence.

`WriteUnpreparedTxn : public WritePreparedTxn` overrides write APIs (`Put`, `Merge`, `Delete`, `SingleDelete`), lifecycle APIs (`PrepareInternal`, `CommitWithoutPrepareInternal`, `CommitInternal`, `RollbackInternal`, `Clear`), savepoint APIs (`SetSavePoint`, `RollbackToSavePoint`, `PopSavePoint`), read APIs (`Get`, `MultiGet`, `GetIterator`), recovery (`RebuildFromWriteBatch`), and conflict validation (`ValidateSnapshot`). Private helpers include `WriteRollbackKeys`, flush helpers, savepoint rollback, and `HandleWrite`.

## Control flow and state behavior

The header documents the iterator/read flow in detail. The read callback passes `CalcMaxVisibleSeq(unprep_seqs, snapshot)` to the parent `ReadCallback` so DB iteration does not filter out the transaction's own unprepared writes too early. `IsVisibleFullCheck` then provides exact visibility. The header also notes an important iterator caveat: max visible sequence is computed when the iterator is created, so later unprepared writes in the same transaction may not appear in that iterator.

Persistent and in-memory transaction state is represented by `unprep_seqs_`, mapping each unprepared or prepared DB write's first sequence to its sub-batch count. `last_log_number_` tracks the last WAL used, while inherited `log_number_` tracks the oldest WAL with uncommitted data. `recovered_txn_` marks transactions rebuilt from recovery shells, for which locks are tracked for rollback but not actually held. `largest_validated_seq_` records how far snapshot validation has proven there are no conflicting committed keys, which is required for safe reverse iteration when own unprepared writes widen visibility.

Savepoint state is split across base `save_points_`, `flushed_save_points_`, and `unflushed_save_points_`. A `SavePoint` stores the `unprep_seqs_` visible at the savepoint and a managed snapshot used to restore old values if rolling back after flushing. Active transaction iterators are stored in `active_iterators_` so they can be invalidated and so flushes can be suppressed while they exist. `untracked_keys_` records keys appended to the underlying batch without normal lock tracking so rollback can still repair them.

## Dependencies and integration points

The header includes `write_prepared_txn.h` and `write_unprepared_txn_db.h`, so the transaction class is intentionally coupled to both write-prepared base behavior and DB-specific iterator/snapshot helpers. It uses `LockTracker`, `WriteBatchWithIndex`, `ManagedSnapshot`, `BaseDeltaIterator`, column-family IDs, RocksDB transaction options, and DB write/read callbacks.

## Risks and edge cases

The header calls out several known risks. Untracked writes can break snapshot validation because checking only the largest sequence for a key can hide smaller committed versions; a TODO proposes either deeper validation or returning `NotSupported`. Savepoint state is redundant and must maintain invariants between flushed and unflushed stacks. Untracked keys are not recorded per savepoint, making rollback less efficient. Active iterators make flushing unsafe because their delta iterator may point into write-batch memory. Reverse iteration is safe only if snapshot validation has excluded committed values between the transaction snapshot and own unprepared sequence numbers.

## Test signals

Friend declarations expose internals to read-your-own-write, recovery, and unprepared-batch tests. The companion test file verifies the documented iterator, savepoint, untracked-key, recovery, and range-tombstone edge cases.
