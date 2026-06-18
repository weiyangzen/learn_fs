# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/TransactionDBTest.java

## Purpose

This suite tests Java `TransactionDB` open paths, transaction creation overloads, transaction reuse, lock-status introspection, deadlock buffer APIs, and simple iterator behavior.

## Important APIs and types

The file uses `TransactionDB`, `TransactionDBOptions`, `TransactionOptions`, `Transaction`, `WriteOptions`, `ReadOptions`, `DBOptions`, `Options`, column-family descriptors/handles, `TransactionDB.KeyLockInfo`, and `RocksIterator`.

## Control flow

Open tests cover plain and column-family variants, plus the error path when the default column family descriptor is missing. Begin tests cover new transactions and reusing an old `Transaction` object. `lockStatusData` writes through a transaction, calls `getForUpdate`, and checks the lock table entry. Deadlock tests inspect or set the deadlock buffer. The iterator test writes one key and iterates through `TransactionDB`.

## State and persistence behavior

The DB is temporary but real. Transaction state includes native transaction handles, write options, locks, and lock-status metadata. The tests do not commit most transaction-open cases, focusing on construction and introspection.

## Dependencies and integration points

This suite links Java transaction wrappers to native transaction DB opening, lock manager data structures, CF descriptor validation, and standard RocksDB iteration.

## Risks and test signals

Risks include default-CF validation gaps, stale transaction reuse, incorrect lock table conversion, and deadlock buffer API regressions. Signals are non-null handles, expected `IllegalArgumentException`, exact lock info fields, and iterator key/value assertions.
