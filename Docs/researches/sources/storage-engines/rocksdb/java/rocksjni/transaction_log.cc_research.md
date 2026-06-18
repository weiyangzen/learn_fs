# sources/storage-engines/rocksdb/java/rocksjni/transaction_log.cc

## Purpose
This file bridges Java `TransactionLogIterator` to C++ `TransactionLogIterator`, allowing Java to iterate WAL transaction log batches.

## Important APIs, Types, and Functions
Exports include `disposeInternalJni`, `isValid`, `next`, `status`, and `getBatch`. It uses `rocksdb/transaction_log.h`, `BatchResult`, and `BatchResultJni::construct`.

## Control Flow
Each method casts the Java `long` handle to `TransactionLogIterator*`. Validity and movement directly call `Valid()` and `Next()`. `status` retrieves iterator status and throws a Java `RocksDBException` on errors. `getBatch` calls `GetBatch()` and constructs the Java `TransactionLogIterator.BatchResult` object through portal conversion.

## State and Persistence Behavior
The iterator reads persistent WAL state from an existing RocksDB instance but does not mutate database contents. `next` advances iterator state. `disposeInternalJni` deletes the native iterator object.

## Dependencies and Integration Points
This bridge integrates with Java APIs that obtain transaction log iterators from RocksDB and then inspect batch sequence numbers and write batches. It depends on RocksJNI portal conversion for batch result construction.

## Risks and Edge Cases
Calling `getBatch` when the iterator is invalid depends on C++ iterator preconditions and Java wrapper discipline. `status` must be checked by callers after iteration. Invalid or double-disposed handles would crash. The returned batch result may contain a write batch handle whose ownership semantics are governed by the portal constructor.

## Test Signals
Tests should write data, obtain updates since a sequence number, iterate batches, verify `isValid` and `next`, inspect returned batch contents, and assert that iterator errors propagate through `status`.
