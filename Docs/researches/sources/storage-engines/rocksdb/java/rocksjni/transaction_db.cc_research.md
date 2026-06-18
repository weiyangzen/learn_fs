# sources/storage-engines/rocksdb/java/rocksjni/transaction_db.cc

## Purpose
This file bridges `org.rocksdb.TransactionDB` to C++ `TransactionDB`. It opens transaction-aware databases, creates transactions, closes and disposes native database handles, and exposes prepared transaction, lock, and deadlock inspection APIs to Java.

## Important APIs, Types, and Functions
Key JNI exports include two `open` overloads, `disposeInternalJni`, `closeDatabase`, transaction creation overloads with optional `TransactionOptions` and reusable old transaction handles, `getTransactionByName`, `getAllPreparedTransactions`, `getLockStatusData`, `getDeadlockInfoBuffer`, and `setDeadlockInfoBufferSize`. It uses `Options`, `DBOptions`, `TransactionDBOptions`, `ColumnFamilyDescriptor`, `ColumnFamilyOptions`, `ColumnFamilyHandle`, `Transaction`, `KeyLockInfo`, `DeadlockPath`, and `DeadlockInfo`.

## Control Flow
The simple open path converts a Java path string, calls `TransactionDB::Open`, releases the string, and returns a DB pointer or throws `RocksDBException`. The column-family open path converts Java `byte[][]` names and `long[]` option handles to descriptor vectors, calls the column-family open overload, and returns a `long[]` whose first element is the DB handle followed by column-family handles. Transaction creation reinterprets write option and transaction option handles and calls `BeginTransaction`. Metadata getters convert native vectors and maps into Java arrays, maps, and nested objects through portal helpers.

## State and Persistence Behavior
Opening creates persistent database state on disk. Begin-transaction calls allocate or reuse C++ transaction objects. `closeDatabase` calls `TransactionDB::Close`, while `disposeInternalJni` deletes the database object. Prepared transaction and lock/deadlock methods expose in-memory transaction manager state. `setDeadlockInfoBufferSize` mutates native diagnostic buffer capacity.

## Dependencies and Integration Points
The bridge depends on `rocksdb/utilities/transaction_db.h`, `rocksdb/options.h`, transaction utilities, and RocksJNI portal conversion helpers. It integrates with Java `TransactionDB`, `Transaction`, `TransactionDBOptions`, `TransactionOptions`, `ColumnFamilyDescriptor`, `ColumnFamilyHandle`, `TransactionDB.KeyLockInfo`, `TransactionDB.DeadlockInfo`, and `TransactionDB.DeadlockPath`.

## Risks and Edge Cases
The column-family open path has many JNI cleanup branches; leaks or missed releases would pin Java arrays or strings. The `beginTransaction_withOld` overload asserts that RocksDB returns the same transaction pointer that Java supplied, which is a critical ownership assumption. `getAllPreparedTransactions` returns raw native transaction pointers without allocating Java-owned C++ transactions. In `getDeadlockInfoBuffer`, the inner `jdeadlock_infos` array length is set from `deadlock_info_buffer.size()` instead of `deadlock_infos.size()`, which can create wrong-sized Java arrays and should be tested. Local references for constructed deadlock objects are not always deleted after array insertion.

## Test Signals
Tests should cover simple open, column-family open result ordering, close error propagation, transaction reuse, named prepared transaction lookup, lock status map conversion, deadlock info array conversion with paths of varying lengths, and deadlock buffer sizing. Recovery tests with prepared transactions are especially relevant because the file returns native transaction handles discovered from the transaction DB.
