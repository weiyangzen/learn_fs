# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TransactionLogIterator.java

## Purpose
`TransactionLogIterator` iterates over RocksDB transaction log batches exposed from the native WAL/transaction log reader. It stops at sequence gaps and returns sequence-numbered `WriteBatch` objects.

## Important APIs and Types
The iterator API includes `isValid()`, `next()`, `status()`, and `getBatch()`. `BatchResult` is a value holder containing a `long sequenceNumber` and a `WriteBatch` constructed from a native handle with ownership enabled.

## Control Flow, State, and Persistence
The iterator wraps a native handle supplied by package-private construction. `getBatch()` asserts validity, calls native `getBatch`, and returns Java objects backed by native batch state. `BatchResult.writeBatch()` exposes the batch object to callers, making resource ownership important. `status()` surfaces native failures as `RocksDBException`.

## Dependencies and Integration Points
The class depends on `RocksObject`, `WriteBatch`, and native WAL iteration JNI. It is normally obtained from DB APIs that expose updates since a sequence number. It integrates with replication, backup, and recovery code that consumes WAL batches.

## Risks and Test Signals
Caller misuse is possible if `getBatch()` is called after invalidation or before checking `status()`. The nested `WriteBatch` owns the native handle and must be closed. This subset contains backup and WAL-related enums but no direct transaction log iterator test; risk is therefore in native binding and lifecycle behavior not visible in Java-only assertions.
