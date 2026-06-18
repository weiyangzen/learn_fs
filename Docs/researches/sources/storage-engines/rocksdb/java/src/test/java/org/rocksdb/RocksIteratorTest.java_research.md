# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/RocksIteratorTest.java

## Purpose

This suite validates Java `RocksIterator` behavior for byte-array accessors, heap/direct `ByteBuffer` accessors, forward and reverse seeking, refresh, snapshot refresh, and iterator lifetime when column-family handles are closed or dropped.

## Important APIs and types

Key types are `RocksIterator`, `RocksDB`, `Options`, `Snapshot`, `ColumnFamilyHandle`, and `ByteBuffer`. Helpers `validateByteBufferResult`, `validateKey`, and `validateValue` assert returned full lengths and destination buffer position/limit behavior.

## Control flow

The tests create small databases, write ordered keys, open iterators, and exercise `seekToFirst`, `seekToLast`, `next`, `prev`, `seek`, `seekForPrev`, `status`, `refresh`, and `refresh(snapshot)`. Byte-array tests cover undersized arrays, offset/length writes, trailing zero preservation, and bounds errors. Byte-buffer tests cover direct buffers, heap buffers, and sliced buffers with nonzero backing offsets.

## State and persistence behavior

Iterator state is native and mutable. Tests confirm iterator validity transitions at beginning/end, snapshot-bound views, refresh visibility after new writes, and iterator independence from later column-family handle close/drop. No durable reopen is tested here.

## Dependencies and integration points

The suite exercises JNI transfer of keys/values from native iterator state into Java arrays and buffers, including correct handling of position/limit and slice offsets. It also validates the relationship among iterators, snapshots, DB mutations, and column-family native handles.

## Risks and test signals

Risks include buffer overrun, wrong returned length for partial copies, stale iterator views after refresh, invalid native ownership after CF close/drop, and incorrect reverse-seek semantics. Signals are exact key/value assertions, validity checks, buffer position/limit checks, and expected `IndexOutOfBoundsException` paths.
