# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/RocksIterator.java

## Purpose
`RocksIterator` is the concrete DB iterator for key/value traversal over a RocksDB column family or DB. It extends `AbstractRocksIterator<RocksDB>` and supplies key/value access plus JNI implementations for seek, movement, refresh, validity, status, and disposal.

## Important APIs and Types
- Constructors are protected and bind a parent `RocksDB` plus native iterator handle.
- Key access: `key()`, `key(byte[])`, `key(byte[], int, int)`, `key(ByteBuffer)`.
- Value access: `value()`, `value(byte[])`, `value(byte[], int, int)`, `value(ByteBuffer)`.
- Native iterator operations override abstract hooks: validity, seek first/last, next/prev, refresh, seek/seekForPrev for arrays and direct buffers, status, and dispose.

## Control Flow
High-level navigation methods are inherited from `AbstractRocksIterator`, which calls the overridden native hooks. `key` and `value` methods assert handle ownership, validate array bounds where offsets are exposed, then invoke JNI. ByteBuffer variants choose direct JNI access for direct buffers and array JNI access for heap buffers, then reduce the buffer limit to the actual returned length or current limit, whichever is smaller.

## State and Persistence Behavior
The iterator owns a native iterator handle and references its parent DB to keep the DB alive while the iterator exists. It does not mutate persistent data; it reads the DB state selected by its creation/read options/snapshot. `refresh` can retarget the native iterator to latest DB state or a supplied snapshot and invalidates positioning until the caller seeks again.

## Dependencies and Integration Points
It depends on `AbstractRocksIterator`, `RocksDB`, `Snapshot`, `RocksDBException`, `ByteBuffer`, and `BufferUtil.CheckBounds`. Instances are produced by `RocksDB.newIterator` and `RocksDB.newIterators`.

## Risks
The public docs require `isValid()` before reading key/value, but Java methods rely on native enforcement. Returned byte arrays copy from native storage, while buffer reads can be partial if the buffer is too small. The ByteBuffer methods set limits rather than advancing positions, so caller expectations must match the contract. Thread safety allows concurrent const methods only; navigation requires external synchronization.

## Test Signals
Tests should verify invalid iterator behavior, key/value copy and partial-buffer lengths, offset validation, direct and heap ByteBuffer paths, position/limit updates, refresh invalidation, status exception propagation, and closing iterators before DB close.
