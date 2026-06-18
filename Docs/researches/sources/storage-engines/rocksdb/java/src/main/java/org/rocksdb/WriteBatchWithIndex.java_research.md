# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WriteBatchWithIndex.java

## Purpose
`WriteBatchWithIndex` augments `WriteBatch` semantics with a searchable key index and read-your-own-writes functionality. It extends `AbstractWriteBatch`.

## Important APIs and Types
Constructors allow default bytewise comparison, configurable duplicate-key overwrite, and custom fallback comparator/reserved bytes. APIs include `newIterator`, `newIteratorWithBase`, `getFromBatch`, `getFromBatchAndDB`, and `getWriteBatch`.

## Control Flow, State, and Persistence
Mutations delegate to native functions that both append to the underlying write batch and update the index. Iterators over batch state return `WBWIRocksIterator`; iterators with a base DB iterator create a merged `RocksIterator` and disown the base iterator because native code takes ownership. `getFromBatch` reads only staged writes and may fail with merge-in-progress if merges cannot be resolved; `getFromBatchAndDB` combines batch and DB state using the DB merge operator.

## Dependencies and Integration Points
Depends on `AbstractWriteBatch`, `AbstractComparator`, `ColumnFamilyHandle`, `RocksIterator`, `ReadOptions`, `DBOptions`, `RocksDB`, `WBWIRocksIterator`, `ByteBuffer`, and JNI. Transactions expose their internal indexed batch through `Transaction.getWriteBatch()`.

## Risks and Test Signals
Updating a batch while using an iterator on the current key can invalidate key/value memory. Delete range is explicitly marked unsupported in `WriteBatchWithIndex` despite native methods existing. Base iterator ownership transfer can surprise callers. `AbstractTransactionTest.getWriteBatch` validates non-owning transaction batch exposure and count; broader read-your-own-writes behavior is covered by transaction get/iterator tests.
