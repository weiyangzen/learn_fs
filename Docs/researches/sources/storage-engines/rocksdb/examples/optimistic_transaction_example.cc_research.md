# sources/storage-engines/rocksdb/examples/optimistic_transaction_example.cc

## Purpose
`optimistic_transaction_example.cc` demonstrates RocksDB's `OptimisticTransactionDB` API, including read-committed behavior, snapshot isolation, conflict detection at commit time, and multiple-snapshot transaction patterns.

## Important APIs and control flow
The example opens an `OptimisticTransactionDB`, obtains the base `DB`, and runs three scenarios. The first starts a transaction, writes `"abc"`, writes conflicting `"abc"` outside the transaction, and shows `Commit()` returning `Busy` while unrelated outside write `"xyz"` succeeds. The second starts a transaction with `set_snapshot=true`, writes `"abc"` outside the transaction, reads the old snapshot value via `GetForUpdate()`, and shows commit conflict. The third advances snapshots within one transaction, writes `"x"`, observes outside write `"y"`, calls `SetSnapshot()`, reads `"y"` for update, updates it, and commits successfully.

## State, persistence, and integration
The DB is under a temp path and is destroyed at the end. The example integrates with `OptimisticTransactionOptions`, `Transaction`, `Snapshot`, base DB reads/writes, and transaction `Get`, `GetForUpdate`, `Put`, `SetSnapshot`, and `Commit`.

## Risks and test signals
The example manually deletes transactions and `txn_db`, so early exits would leak. Snapshot pointers must be cleared from `ReadOptions` after transaction deletion, which the example does. Unlike pessimistic transactions, outside conflicting writes are not locked out and conflicts surface at commit. Test signals are expected `IsBusy()` statuses for conflicts, successful read of committed outside values, successful final commit after snapshot advancement, and clean `DestroyDB()`.
