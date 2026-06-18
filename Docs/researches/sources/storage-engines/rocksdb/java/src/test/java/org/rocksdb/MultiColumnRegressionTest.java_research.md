## sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/MultiColumnRegressionTest.java

### Purpose

`MultiColumnRegressionTest` is a regression test for transactional multi-column-family problems referenced by RocksDB issue 9006. It checks transaction reads/writes across several column-family handles with both normal and extremely long CF names.

### Important APIs, Types, And Functions

The test uses parameterized `Params(numColumns, keySize)`, `TransactionDB.open`, `OptimisticTransactionDB.open`, `Transaction.put`, `Transaction.get`, `Transaction.commit`, `ColumnFamilyDescriptor`, `ColumnFamilyHandle`, `DBOptions`, and `TransactionDBOptions`.

### Control Flow

For `TransactionDB`, it builds `numColumns` descriptors whose names include a long repeated suffix, creates them in a plain `RocksDB`, reopens as `TransactionDB` with those descriptors plus default, writes one key per CF and one default key in a transaction, commits, reopens, and reads each CF key in a new transaction. For optimistic transactions, descriptors are intentionally all named `"default"` plus another default descriptor, then an `OptimisticTransactionDB` writes and rereads through the returned handles.

### State And Persistence Behavior

The test persists CF metadata and transaction writes across close/reopen. It verifies that handle ordering and native column-family identity remain consistent despite large descriptor names and repeated descriptor names in the optimistic path.

### Dependencies And Integration Points

It integrates JUnit parameterization, RocksDB CF creation/opening, `TransactionDB`, `OptimisticTransactionDB`, and transaction read/write APIs.

### Risks And Edge Cases

- The optimistic test uses duplicate default CF names, which may target wrapper regression coverage but is unusual compared with normal CF usage.
- Handles must be closed manually after transaction DB close scopes; leaks or wrong close order would affect JNI resource lifetime.
- Long CF names stress native vector/string handling and Java array marshalling.

### Test Signals

Each CF key must return `"value" + (i - 7)` after reopen, for both moderate and very large CF-name sizes. Static research only; no test command was run.
