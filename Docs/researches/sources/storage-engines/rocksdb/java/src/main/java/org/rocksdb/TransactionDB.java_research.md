# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TransactionDB.java

## Purpose
`TransactionDB` is the RocksJava database wrapper for pessimistic transaction support. It opens transaction-capable RocksDB instances, begins transactions, recovers prepared transactions, exposes lock/deadlock diagnostics, and manages native DB lifecycle.

## Important APIs and Types
Static `open` overloads support simple `Options` and multi-column-family `DBOptions`/`ColumnFamilyDescriptor` opening with `TransactionDBOptions`. Transaction APIs implement `TransactionalDB<TransactionOptions>`: `beginTransaction(WriteOptions)`, `beginTransaction(WriteOptions, TransactionOptions)`, and old-transaction reuse overloads. Recovery/diagnostics include `getTransactionByName`, `getAllPreparedTransactions`, `getLockStatusData`, `getDeadlockInfoBuffer`, and `setDeadlockInfoBufferSize`. Nested DTOs are `KeyLockInfo`, `DeadlockInfo`, and `DeadlockPath`.

## Control Flow
`open(Options, ...)` calls native open, stores Java option references to prevent GC, stores transaction options, and creates/stores the default column family handle. The multi-CF open builds native arrays of column-family names and option handles, verifies the default column family is present, calls native open, wraps returned handles, records ownership, and stores the default CF. `closeE` closes native DB with exception propagation, while `close` first closes owned column-family handles and suppresses close errors. `beginTransaction` wraps native transaction handles. Old-transaction reuse asserts native returns the same handle. Named/prepared transaction lookups wrap non-owned transaction handles and call `disOwnNativeHandle`.

## State and Persistence Behavior
The class owns a native `TransactionDB` handle and Java references to options and transaction DB options. Persistent DB state lives on disk at the opened path. Transactions commit through native RocksDB; prepared transactions may survive process restart and be retrieved by name/all-prepared APIs. Lock and deadlock information is diagnostic in-memory native state.

## Dependencies and Integration Points
It extends `RocksDB`, implements `TransactionalDB<TransactionOptions>`, and depends on `Options`, `DBOptions`, `TransactionDBOptions`, `ColumnFamilyDescriptor`, `ColumnFamilyHandle`, `WriteOptions`, `TransactionOptions`, `Transaction`, and native JNI functions.

## Risks and Test Signals
Tests should cover simple and multi-CF opens, missing default-CF validation, option lifetime retention, close vs `closeE`, transaction begin with and without options, old-transaction reuse assumptions, prepared transaction lookup ownership, lock-status map construction, deadlock buffer shape/limit behavior, and restart recovery for prepared transactions. Risks include non-owned transaction wrappers being closed incorrectly, default-CF handle ownership ordering, and native open overload drift.
