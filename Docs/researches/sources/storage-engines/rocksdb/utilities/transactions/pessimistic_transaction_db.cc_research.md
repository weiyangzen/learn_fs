# sources/storage-engines/rocksdb/utilities/transactions/pessimistic_transaction_db.cc

## Purpose

This file implements the stackable `TransactionDB` layer for pessimistic transactions. It wraps `DBImpl`, validates options/column families, prepares open-time two-phase-commit prerequisites, selects write policy subclasses, coordinates lock-manager CF state, wraps direct DB writes in internal transactions, reconstructs recovered prepared transactions, tracks expirable/named transactions, and delegates timestamped snapshot APIs to `DBImpl`.

## Important APIs And Functions

- Constructors resolve `DBImpl`, store `TransactionDBOptions`, and create a `LockManager`.
- `Initialize()` registers CFs, verifies timestamp options, re-enables compaction, enables published sequence tracking for write-committed, and rebuilds recovered transactions.
- `VerifyCFOptions()` permits timestamped CFs only when timestamp size is `sizeof(TxnTimestamp)` and write policy is `WRITE_COMMITTED`.
- `TransactionDB::Open()` rejects incompatible unordered-write combinations, calls `PrepareWrap()`, opens `DBImpl`, and wraps it through `WrapDB()`.
- `PrepareWrap()` enables memtable history, temporarily disables compaction during open, and sets `allow_2pc`.
- `WrapAnotherDBInternal()` constructs `WriteUnpreparedTxnDB`, `WritePreparedTxnDB`, or `WriteCommittedTxnDB`.
- Direct `Put`, `PutEntity`, `Delete`, `SingleDelete`, `Merge`, and `Write` enforce locking by internal transactions unless concurrency control is explicitly skipped.
- Timestamped snapshot methods delegate to `DBImpl`.

## Control Flow

Open-time control flow prepares column-family descriptors and DB options for transaction correctness, opens the root DB with policy-specific sequence settings, then initializes the transaction wrapper. Initialization converts recovered shell transactions into real transaction objects using sync writes and `skip_concurrency_control=true`, sets log numbers/names, rebuilds batches, marks them `PREPARED`, and clears shell recovery state on success.

Direct writes create an internal transaction, disable indexing, apply an untracked operation, commit, and delete the transaction. Batch writes use `WriteWithConcurrencyControl()`, which locks all keys in deterministic order through `CommitBatch()`.

## State And Persistence Behavior

The wrapper owns in-memory coordination state: `lock_manager_`, `column_family_mutex_`, `expirable_transactions_map_`, `transactions_`, DB options, and logger. Durable transaction information lives in WAL/memtable/recovery state owned by `DBImpl`; this class reconstructs transaction objects from that state during open.

Timestamped snapshots are shared DB snapshots. `CreateTimestampedSnapshot()` rejects `kMaxTxnTimestamp`; `SnapshotCreationCallback` creates commit-time snapshots at the sequence passed from `WriteImpl()`.

## Dependencies And Integration Points

The file integrates `DBImpl`, lock managers, `TransactionDBMutexFactory`, write-prepared/write-unprepared DBs, `SecondaryIndexMixin`, `WriteBatchInternal`, logging, mutex utilities, and sync points. It is the central bridge between public `TransactionDB` APIs and internal RocksDB transaction machinery.

## Risks And Test Signals

Risks include missing memtable history, timestamped direct writes bypassing transaction APIs, unsafe `skip_concurrency_control`, recovery relying on external serialization, CF lock-map drift, and the destructor TODO around deleting entries from `transactions_`. Timestamped snapshot tests cover snapshot APIs here; broader transaction tests cover open/recovery/direct-write locking.
