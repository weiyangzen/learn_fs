# sources/storage-engines/rocksdb/utilities/transactions/write_unprepared_txn_db.cc

## Purpose

`write_unprepared_txn_db.cc` implements the DB wrapper for the write-unprepared policy. It extends write-prepared DB initialization, converts recovered prepared records into live `WriteUnpreparedTxn` objects, rolls back recovered unprepared records directly, and creates DB iterators that can expose the owning transaction's unprepared writes while preserving write-prepared visibility checks.

## Important APIs, types, and functions

`RollbackRecoveredTransaction` restores DB state for transactions that crashed while still unprepared. `Initialize` sets snapshot/recoverable-state callbacks, registers column families, verifies options, rebuilds prepared recovered transactions, populates prepared sequence metadata, advances max-evicted state, rolls back unprepared recovered transactions, deletes recovery shells, and re-enables compaction. `BeginTransaction` creates or reinitializes `WriteUnpreparedTxn`. `IteratorState` owns a `WriteUnpreparedTxnReadCallback` and optional managed snapshot for DB iterator cleanup. `NewIterator(ReadOptions, ColumnFamilyHandle*, WriteUnpreparedTxn*)` constructs the DB-side iterator used by transaction iterators.

## Control flow and state behavior

During direct rollback of recovered unprepared transactions, batches are processed in reverse sequence order. For each recovered batch, `RollbackWriteBatchBuilder` deduplicates keys per column family using the appropriate comparator, reads the value visible immediately before that batch (`last_visible_txn = batch_seq - 1`), and writes either the old value or a delete into a rollback batch. Merge operands are rolled back only if `rollback_merge_operands` is enabled. A rollback marker is appended and written to DB. In two-write-queue mode the last published sequence is updated manually.

Initialization first installs a `WritePreparedSnapshotChecker` and a recoverable-state pre-release callback that marks recovered-state sub-batches as committed. It then performs the base transaction DB setup: add column families, verify options, remember which column families need compaction re-enabled. For recovered prepared transactions, it creates a real write-unprepared transaction, marks it as recovered, sets log number, ID, name, prepare batch count, records every recovered batch in `unprep_seqs_`, rebuilds tracked keys from each batch, clears the working batch, and marks it `PREPARED`. It separately gathers all recovered prepare sequence ranges in ordered form and calls `AddPrepared` in sequence order.

After recovered prepared metadata is registered, `Initialize` advances `max_evicted_seq_` to the DB latest sequence and creates a sequence gap after recovery by setting last allocated, last sequence, and last published sequence to `last_seq + 1` when nonzero. Only then does it roll back recovered unprepared transactions. Compaction is re-enabled after prepared/unprepared recovery is resolved because compaction needs correct snapshot and prepare metadata to avoid preserving or dropping the wrong versions.

`NewIterator` ensures `ReadOptions::io_activity` is compatible, obtains or creates a snapshot, and rejects iterator creation if the transaction has unprepared writes and `largest_validated_seq_` is newer than the chosen snapshot. That guard protects `Prev()` semantics: reverse iteration can otherwise stop too early when committed values exist between snapshot sequence and own unprepared sequence. The DB iterator is created with `MaxVisibleSeq()` from the callback, making own unprepared writes reachable, and cleanup deletes `IteratorState`.

## Dependencies and integration points

The implementation uses `DBImpl::recovered_transactions`, `DBImpl::WriteImpl`, `logs_with_prep_tracker`, `VersionSet` sequence setters, column-family handles and comparators, `ArenaWrappedDBIter`, `ColumnFamilyHandleImpl`, `SuperVersion`, `ManagedSnapshot`, and the write-prepared snapshot checker. It relies on `WriteUnpreparedTxn` internals through friendship and on write-prepared metadata functions such as `AddPrepared`, `AdvanceMaxEvictedSeq`, and `GetCFHandleMap`.

## Risks and edge cases

Recovery ordering is critical. `AddPrepared` must happen before advancing max-evicted sequence, and unprepared rollback must happen only after max-evicted state can preserve snapshot decisions. The direct rollback path intentionally writes rollback records to WAL even during recovery because application XIDs might not be unique across restarts; disabling WAL could let later recovered transactions with the same name resurrect rolled-back data. Iterator creation can return `nullptr` for unvalidated writes, so callers must handle that failure. Rollback builder depends on comparator-aware deduplication and currently has TODOs for IO priority plumbing.

## Test signals

`RecoveryTest` verifies prepared recovered transactions are exposed by `GetAllPreparedTransactions` and can later commit or roll back, while unprepared recovered transactions are not exposed and are rolled back. Iterator behavior is exercised by read-your-own-write, no-snapshot, reverse iteration, and range-tombstone tests.
