# sources/storage-engines/rocksdb/test_util/transaction_test_util.cc

Purpose: implements `RandomTransactionInserter`, a transaction stress helper that repeatedly increments one random key in each key set and verifies that all sets retain equal totals.

Important APIs/control flow: `TransactionDBInsert()` begins/reuses a transaction, assigns a unique thread/id-derived name, sometimes sets a snapshot, and calls `DoInsert()`. `OptimisticTransactionDBInsert()` does the same for optimistic transactions. `DBInsert()` writes through a plain `WriteBatch`. `DBGet()` formats keys as four-digit set prefix plus random key number, reads through transaction or DB, parses numeric values, and treats not found as zero. `DoInsert()` shuffles set order, chooses an increment, gets/deletes/puts per set, optionally prepares, maybe writes commit-time batch data, commits or rolls back, and records success/failure/bytes/status. `Verify()` sums each set through point lookups or iterators and reports corruption when totals differ.

State behavior: the inserter owns reusable `Transaction*` and `optimistic_txn_` pointers, counters, last status, mutable read options, and transaction IDs. It uses snapshots only within a call and releases verification snapshots.

Dependencies/integration: integrates with `DB`, `TransactionDB`, `OptimisticTransactionDB`, transaction options, snapshots, logging, thread IDs, and RocksDB random utilities.

Risks and test signals: the helper assumes the DB starts empty and values are decimal integers. `DoInsert()` logs/asserts around transaction expectations and treats some conflict statuses as expected. `RollbackDeletionTypeCallback()` mirrors the delete-vs-single-delete rule based on set index. Tests should cover concurrent transaction stress, optimistic conflict handling, prepared commit paths, rollback paths, snapshot verification delays, and invariant failure detection.
