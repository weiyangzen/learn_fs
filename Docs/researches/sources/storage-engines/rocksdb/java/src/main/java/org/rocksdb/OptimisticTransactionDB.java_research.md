# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/OptimisticTransactionDB.java research

## Purpose

`OptimisticTransactionDB` is the Java wrapper for RocksDB's optimistic transaction database. It extends `RocksDB` and implements `TransactionalDB<OptimisticTransactionOptions>`, adding transaction creation and optimistic conflict handling support through native code.

## Important APIs and types

Static `open(Options, String)` opens a default-column-family DB and stores the `Options` reference plus default handle. Static `open(DBOptions, String, List<ColumnFamilyDescriptor>, List<ColumnFamilyHandle>)` opens multiple column families, validates that the default column family descriptor is present, fills caller-provided handles, records owned handles, and stores the default handle. `beginTransaction(...)` overloads create new `Transaction` wrappers or reuse an existing transaction. `getBaseDB()` returns a disowned `RocksDB` wrapper around the underlying base DB.

## Control flow

Open methods marshal option and column-family handles into native arrays, call native `open`, then build Java wrappers around returned handles. Reusing `oldTransaction` asserts native returned the same handle. `close()` closes owned column-family handles, clears the list, closes the native DB while swallowing exceptions, and disposes. `closeE()` propagates close errors but directly closes the DB handle.

## State and persistence behavior

The object owns a native optimistic transaction DB handle and column-family handles. Transactions write to the same persistent RocksDB storage as ordinary writes but check conflicts at commit time. Closing does not fsync WAL files; callers needing durability must sync WAL or issue a sync write first.

## Dependencies and integration points

It depends on `Options`, `DBOptions`, `ColumnFamilyDescriptor`, `ColumnFamilyHandle`, `WriteOptions`, `OptimisticTransactionOptions`, `Transaction`, and base `RocksDB` ownership helpers. It is used by Java clients needing transactional write batches without pessimistic locks.

## Risks and test signals

Risks include missing default column-family descriptors, handle ownership mistakes, close-vs-closeE differences, reused transaction lifecycle ambiguity, and durability assumptions on close. Tests should cover single-CF and multi-CF open, default CF validation, begin/commit conflict behavior, transaction reuse assertions, base DB wrapper disowning, and close ordering with outstanding handles.
