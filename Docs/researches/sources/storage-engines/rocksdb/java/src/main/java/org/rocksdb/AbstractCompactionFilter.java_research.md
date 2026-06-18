# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractCompactionFilter.java

## Purpose
This Java base class represents a compaction filter backed by a native C++ implementation. It lets Java API users hold and dispose a native filter while exposing compaction context metadata.

## Important APIs, Types, and Functions
`AbstractCompactionFilter<T extends AbstractSlice<?>>` extends `RocksObject`. Its nested `Context` class stores `fullCompaction` and `manualCompaction` booleans with accessors `isFullCompaction` and `isManualCompaction`. The protected constructor accepts a native handle. `disposeInternal(long handle)` is a final native method.

## Control Flow
Subclasses are constructed with native handles produced elsewhere, often through a factory callback. Java calls close/dispose through `RocksObject`, which invokes the final native dispose method for the handle.

## State and Persistence Behavior
The class stores native object ownership through `RocksObject.nativeHandle_`. Disposal deletes the underlying C++ compaction filter pointer. The context object is immutable and describes one compaction invocation. Filtering can affect persistent DB contents during compaction, but this base class does not implement filtering logic itself.

## Dependencies and Integration Points
It integrates with compaction filter factories, native compaction filter callback bridges, `AbstractSlice` implementations, and RocksDB options that accept compaction filters.

## Risks and Edge Cases
The documentation warns that disposing while any RocksDB instance still references the filter causes undefined behavior. Because the native dispose method is final, subclasses cannot customize cleanup. Generic type `T` documents slice type but this file does not enforce callback behavior.

## Test Signals
Tests should verify context flag accessors, disposal after DB close, and that premature disposal is avoided by option/DB lifecycle tests. Factory-driven tests should confirm filters are disowned when C++ takes ownership.
