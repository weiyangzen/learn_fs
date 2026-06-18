# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TransactionOptions.java

## Purpose
`TransactionOptions` wraps native per-transaction options and implements the shared `TransactionalOptions<TransactionOptions>` contract. It configures snapshot creation, deadlock detection, lock timeout, expiration, deadlock traversal depth, and maximum write batch size.

## Important APIs and Types
Key methods include `isSetSnapshot/setSetSnapshot`, `isDeadlockDetect/setDeadlockDetect`, `get/setLockTimeout`, `get/setExpiration`, `get/setDeadlockDetectDepth`, and `get/setMaxWriteBatchSize`. Fluent setters return `this`.

## Control Flow, State, and Persistence
Construction initializes native state through `newTransactionOptions()`. Most methods assert ownership before native access, though the later deadlock-depth and write-batch-size methods do not assert explicitly. Java persists no local copies; the native handle owns all option state. Expiration and lock timeout settings affect transaction lock retention and commit validity.

## Dependencies and Integration Points
The class depends on `RocksObject`, `TransactionalOptions`, `Transaction`, `TransactionDBOptions`, and JNI. It is consumed by `TransactionalDB.beginTransaction(WriteOptions, T)` implementations, including regular and optimistic transactions.

## Risks and Test Signals
Important risks are deadlocks when lock timeouts are unbounded, forgotten transactions retaining locks when expiration is unset, and disposed-handle misuse. `AbstractTransactionTest` covers snapshot setting, transaction begin, commit/rollback, lock timeout mutation via `Transaction.setLockTimeout`, and write option behavior, but not every `TransactionOptions` property directly.
