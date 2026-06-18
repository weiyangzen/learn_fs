# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/WBWIRocksIterator.java

## Purpose
`WBWIRocksIterator` iterates over entries in a `WriteBatchWithIndex`. It adapts native indexed write-batch iteration to the shared `AbstractRocksIterator` API and exposes entry type, key, and optional value.

## Important APIs and Types
The central API is `entry()`, which returns a reusable `WriteEntry`. `WriteType` maps native operation ids for put, merge, delete, single delete, delete range, log, and XID. `WriteEntry` exposes `getType`, `getKey`, `getValue`, `equals`, `hashCode`, and `close`.

## Control Flow, State, and Persistence
`entry()` calls native `entry1`, interprets the returned pointer array as type/key/value, and resets two `DirectSlice` wrappers. The returned `WriteEntry` is only valid until iterator repositioning and is not thread-safe because fields are updated non-atomically. All movement, seeking, status, and refresh operations delegate to JNI methods required by `AbstractRocksIterator`. `close()` releases the reusable entry slices before closing the iterator.

## Dependencies and Integration Points
Depends on `AbstractRocksIterator<WriteBatchWithIndex>`, `DirectSlice`, `ByteBuffer`, and native iterator methods. It is created by `WriteBatchWithIndex.newIterator` and can be used to inspect uncommitted batch contents.

## Risks and Test Signals
Risks include stale slices after movement, null value for delete/log entries, non-thread-safe reuse, and enum id drift. `WriteEntry.hashCode` relies on key string representation and may not fit exotic comparators. This subset has indirect transaction write-batch inspection via `AbstractTransactionTest.getWriteBatch`, but no direct `WBWIRocksIterator` assertions.
