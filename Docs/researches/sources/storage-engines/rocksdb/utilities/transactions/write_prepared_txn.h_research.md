# sources/storage-engines/rocksdb/utilities/transactions/write_prepared_txn.h

## Purpose

This header declares `WritePreparedTxn`, the transaction object used by `WritePreparedTxnDB`. Its extensive file-level comment documents the core design: write-prepared 2PC writes user data to memtable and WAL during prepare, records the prepare sequence as uncommitted, and later commits by writing a WAL-only commit marker whose sequence becomes the commit timestamp. Readers use `LastPublishedSequence` plus the write-prepared commit map to distinguish committed and uncommitted memtable entries.

The header also explains why two write queues are useful. Prepare goes through the main write queue because it inserts into memtables, while commit can often go through a nonmem WAL-only queue. This lets serial commit markers avoid waiting behind heavier prepare-time memtable insertion, especially in MySQL-style 2PC workloads.

## Public API surface

`WritePreparedTxn` derives from `PessimisticTransaction`. It deletes copying, has a virtual destructor, and exposes overridden transaction APIs:

- `Get()` and `MultiGet()` use write-prepared snapshot semantics where read visibility is based on the last published WAL sequence rather than simply the latest memtable sequence.
- `GetIterator()` overloads return iterators that combine a write-prepared DB iterator with the transaction's local write batch.
- `GetCoalescingIterator()` and `GetAttributeGroupIterator()` are declared but implemented as unsupported for write-prepared/write-unprepared transactions.
- `SetSnapshot()` is overridden so transaction snapshots are enhanced with `min_uncommitted_`.

The protected `Initialize()` override ensures transaction-specific state is reset, and `SetId()` is made visible to friend classes while still routing to `Transaction::SetId()`.

## Private API surface and state

Private overrides define the lifecycle:

- `GetImpl()` applies write-prepared read callbacks for single-key reads.
- `PrepareInternal()` writes the prepared batch to WAL and memtable and registers prepared sequence numbers.
- `CommitWithoutPrepareInternal()` and `CommitBatchInternal()` support single-phase writes through the write-prepared DB.
- `CommitInternal()` writes commit metadata and publishes the prepared data.
- `RollbackInternal()` writes compensating rollback data and publishes both rollback and prepared entries consistently.
- `ValidateSnapshot()` checks write conflicts using write-prepared visibility.
- `RebuildFromWriteBatch()` rebuilds local transaction state and recalculates sub-batch count.

The class stores `WritePreparedTxnDB* wpt_db_` and `size_t prepare_batch_cnt_`. The DB pointer is the gateway to visibility state, snapshot creation, commit map updates, and comparator maps. `prepare_batch_cnt_` records how many prepare sequence slots the transaction owns when duplicate keys split a write batch into sub-batches.

Friend declarations allow the DB implementation, write-unprepared variants, and selected tests to access internals needed for recovery and white-box validation.

## Control flow documented by the header

The comment's sequence-number table is the clearest contract. Before prepare, last sequence, allocated sequence, and published sequence are equal. Prepare allocates a new sequence, writes WAL and memtable, advances last sequence, but does not advance published sequence because the data is uncommitted. Commit allocates another sequence, writes only a commit marker to WAL in the usual case, updates the commit cache in a pre-release callback, then advances published sequence so readers can observe the commit.

This distinction means snapshots and readers must use `LastPublishedSequence` and write-prepared callbacks, not just the latest assigned sequence. It also means commit ordering and callback ordering are part of correctness, not just performance.

## Dependencies and integration points

The header includes RocksDB public APIs (`db.h`, `snapshot.h`, `transaction.h`, `transaction_db.h`, `write_batch_with_index.h`) and internal transaction infrastructure (`pessimistic_transaction.h`, `pessimistic_transaction_db.h`, `transaction_base.h`, `transaction_util.h`) plus write callback support. It forward-declares `WritePreparedTxnDB` to avoid a circular dependency while allowing the implementation file to connect transaction lifecycle operations to DB-level state.

## State and persistence behavior

The header describes a persistent marker protocol: prepared data is durable after phase 1 because WAL is enabled and memtable data exists at `prepare_seq`; commit is durable after phase 2 because a commit marker is written at `commit_seq`; the in-memory commit map publishes `prepare_seq -> commit_seq` for reads, compaction, and snapshot checks. The class state itself is small because most persistence and visibility state lives in `WritePreparedTxnDB`.

## Risks

Any change that makes reads use ordinary DB snapshots without `LastPublishedSequence` can expose prepared-but-uncommitted data. Any change that routes prepare away from memtable insertion or commit toward unnecessary memtable insertion changes the write-prepared performance and correctness model. The comment also points to two-write-queue ordering: if commit markers are published out of order, readers may observe gaps where prior sequences are not yet publishable.

## Test signals

The design declared here is validated by `write_prepared_transaction_test.cc`. Important signals are `TxnInitialize` for virtual initialization and enhanced snapshots, `Iterate` for iterator behavior, `BasicRecovery` for marker persistence, `SeqAdvanceConcurrent` for sequence accounting, and `MaxCatchupWithNewSnapshot` for the published-sequence versus max-evicted sequence invariant.
