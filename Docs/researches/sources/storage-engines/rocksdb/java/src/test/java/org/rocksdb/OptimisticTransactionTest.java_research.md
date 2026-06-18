## sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/OptimisticTransactionTest.java

### Purpose

`OptimisticTransactionTest` extends shared transaction tests with optimistic-transaction-specific behavior: unsupported prepare/two-phase commit, conflict detection for `getForUpdate` and multi-get-for-update, undoing tracked keys, transaction naming restrictions, and DB container setup.

### Important APIs, Types, And Functions

It uses `AbstractTransactionTest`, `OptimisticTransactionDB`, `OptimisticTransactionOptions`, `Transaction`, `getForUpdate`, `multiGetForUpdate`, `multiGetForUpdateAsList`, `undoGetForUpdate`, `commit`, `setName`, `Status.Code.Busy`, and `Status.Code.InvalidArgument`.

### Control Flow

Tests first establish committed baseline values, then run overlapping transactions. One transaction reads keys for update, another writes and commits conflicting changes, and the first transaction must fail on commit with `Busy`. Undo tests call `undoGetForUpdate` before the conflicting write and then commit successfully. The prepare test confirms optimistic transactions reject `prepare`, and the name test confirms `setName` is invalid.

### State And Persistence Behavior

Committed writes persist in the temporary DB. Optimistic transactions track read-for-update conflict state client-side/native-side until commit. Undo operations remove keys from the conflict set without rolling back any DB write. The container opens default and test CFs with distinct string-append merge operators and closes options, handles, write options, transaction options, and DB.

### Dependencies And Integration Points

The file integrates with shared transaction test infrastructure, CF merge options, optimistic transaction native conflict checking, deprecated and current multi-get APIs, and status-code propagation through `RocksDBException`.

### Risks And Edge Cases

- Optimistic transactions do not support two-phase commit; callers must not assume parity with `TransactionDB`.
- Deprecated array-returning multi-get APIs are still covered alongside list APIs.
- `undoGetForUpdate` must match CF-aware and default-CF key tracking exactly, or conflicts may be missed or falsely retained.
- Resource close order in the custom container is important for native handle ownership.

### Test Signals

Expected signals are `Busy` on conflicting commits, successful commits after undo, an error message for prepare, and `InvalidArgument` for transaction names. Static research only; no test command was run.
