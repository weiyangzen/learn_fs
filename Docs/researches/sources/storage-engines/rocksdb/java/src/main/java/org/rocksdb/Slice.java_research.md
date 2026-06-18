# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Slice.java

## Purpose
`Slice` is the byte-array-backed concrete `AbstractSlice<byte[]>`. It wraps native RocksDB slice memory and is optimized for small keys and values; larger data may use `DirectSlice`.

## Important APIs and Types
- Extends `AbstractSlice<byte[]>`.
- Tracks `cleared` and `internalBufferOffset`.
- Private no-arg constructor for JNI-created Java objects without an initial native object.
- Package constructors for native handles with borrowed or explicit ownership.
- Public constructors from `String`, `byte[]`, and `byte[]` plus offset.
- Overrides `clear()`, `removePrefix(int)`, `disposeInternal()`, and native `data0(long)`.

## Control Flow
Public constructors allocate a native slice from copied Java data. `clear()` calls native clear with whether an internal buffer still needs freeing, then marks the slice cleared. `removePrefix` adjusts the native slice and increments `internalBufferOffset` so disposal knows where the original internal allocation begins. `disposeInternal` frees buffered data if not already cleared, then disposes the native slice pointer through the superclass path.

## State and Persistence Behavior
The Java object owns or borrows a native slice pointer and may own an internal native buffer copied from Java data. It is transient memory, not persisted storage. If used by RocksDB instances or options, its lifetime must outlast native consumers.

## Dependencies and Integration Points
It depends on `AbstractSlice`, native slice allocation/free functions, and RocksDB APIs that accept `Slice` or `Range` boundaries. It integrates with `RocksDB.toRangeSliceHandles`, approximate-size queries, table-property range queries, and suggested compaction ranges.

## Risks
Memory ownership is delicate. Disposing while a DB still references a slice is documented as undefined behavior. `removePrefix` changes disposal offset and must stay synchronized with native allocation semantics. The private JNI constructor relies on external native setup and disowned ownership semantics.

## Test Signals
Tests should cover data round trips from string/byte arrays, offset constructor behavior, `removePrefix` data and disposal correctness, idempotent `clear`, borrowed-handle no double-free behavior, and lifecycle with range-consuming DB APIs.
