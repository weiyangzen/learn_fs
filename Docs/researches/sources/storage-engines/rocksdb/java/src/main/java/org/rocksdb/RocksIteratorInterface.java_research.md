# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/RocksIteratorInterface.java

## Purpose
`RocksIteratorInterface` defines the common traversal contract for iterators over RocksDB-backed sources such as DBs and write batches. It isolates navigation, validity, status checking, and refresh behavior from concrete iterator implementations.

## Important APIs and Types
- Positioning: `seekToFirst()`, `seekToLast()`, `seek(byte[])`, `seekForPrev(byte[])`, `seek(ByteBuffer)`, `seekForPrev(ByteBuffer)`.
- Movement: `next()`, `prev()`.
- State/error: `isValid()`, `status()`.
- Refresh: `refresh()` and `refresh(Snapshot)`.

## Control Flow
Implementations maintain a current cursor. Seek methods establish a valid or invalid position based on target and source contents. `next` and `prev` require a valid iterator and move forward/backward. `status` reports deferred native errors. Refresh changes the DB state the iterator reads and invalidates the cursor until a future seek.

## State and Persistence Behavior
The interface itself has no state. It describes read-only cursor state over persistent or batch-backed data. Snapshot refresh pins a stable DB state for future reads.

## Dependencies and Integration Points
It depends on `ByteBuffer`, `Snapshot`, and `RocksDBException`. `AbstractRocksIterator`, `RocksIterator`, and write-batch iterator implementations are expected consumers.

## Risks
The interface documents direct-buffer support for ByteBuffer seek methods, but enforcement is implementation-specific. Callers must observe `isValid()` preconditions before movement or key/value access on concrete iterators. Refresh support may vary and can throw when unsupported.

## Test Signals
Contract tests should exercise seek boundary cases, forward/backward traversal, invalid movement, status error propagation, refresh invalidation, and ByteBuffer directness requirements across every implementation.
