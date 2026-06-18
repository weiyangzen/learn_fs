# sources/storage-engines/rocksdb/utilities/transactions/pessimistic_transaction_db.h

## Purpose

This header declares `PessimisticTransactionDB`, `WriteCommittedTxnDB`, and `SnapshotCreationCallback`. It defines the interface between public `TransactionDB` operations, lock-manager coordination, transaction creation/reuse, CF lifecycle, transaction recovery maps, direct-write concurrency control, and timestamped snapshots.

## Important APIs, Types, And Members

`PessimisticTransactionDB` declares initialization and validation, pure virtual `BeginTransaction`, direct write overrides, CF creation/drop/import methods, lock-manager facade methods, expirable transaction map methods, named/prepared transaction map methods, and timestamped snapshot APIs. It also provides inline `WriteWithConcurrencyControl()`, `FailIfBatchHasTs()`, and `FailIfCfEnablesTs()`.

Members include `DBImpl* db_impl_`, `info_log_`, immutable `txn_db_options_`, `lock_manager_`, `column_family_mutex_`, `expirable_transactions_map_`, and `transactions_`, with separate mutexes for map protection.

`WriteCommittedTxnDB` overrides `BeginTransaction()` and both `Write()` forms. `SnapshotCreationCallback` derives from `PostMemTableCallback` and carries DB, commit timestamp, notifier, and output snapshot reference.

## Control Flow And Design

The base class owns shared pessimistic DB behavior, while subclasses supply policy-specific transactions. The inline direct-write path updates protection info, begins a temporary transaction, disables indexing, and uses `CommitBatch()` so raw DB writes still acquire locks.

Timestamp helper methods define the public boundary: timestamped writes must go through transaction APIs, not direct `TransactionDB` writes.

## State And Persistence Behavior

Most declared members are runtime coordination state. WAL/memtable/snapshot persistence is owned by `DBImpl` and concrete transaction implementations. `GetAllPreparedTransactions()` is marked not thread-safe and intended for single-threaded recovery use.

## Dependencies And Integration Points

The header pulls together public RocksDB DB/options/transaction APIs, internal DB iter/read callback/snapshot checker types, point and range lock managers, pessimistic transaction types, and write-prepared transaction declarations. Virtual comparator-map hooks are for subclasses that need CF comparator metadata without adding base fast-path overhead.

## Risks And Test Signals

Risks include ensuring every direct write locks all keys, keeping timestamp rejection consistent with transaction timestamp support, avoiding concurrent use of recovery-only APIs, and updating lock-manager CF maps on every CF lifecycle path. Friend tests indicate coverage for recovery/crash scenarios; timestamped snapshot tests use the declared snapshot APIs.
