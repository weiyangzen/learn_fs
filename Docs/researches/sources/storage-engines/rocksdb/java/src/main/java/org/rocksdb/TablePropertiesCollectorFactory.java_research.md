# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TablePropertiesCollectorFactory.java

## Purpose
`TablePropertiesCollectorFactory` is the Java handle wrapper for native table-properties collector factories, including RocksDB's compact-on-deletion collector.

## Important APIs and Types
The abstract class extends `RocksObject` with a private native-handle constructor. `NewCompactOnDeletionCollectorFactory(long sliding_window_size, long deletion_trigger, double deletion_ratio)` allocates a native compact-on-deletion factory and returns an anonymous subclass that deletes it. `newWrapper(long)` wraps an existing native handle for internal use.

## Control Flow
Factory construction delegates to native allocation. The returned anonymous subclass implements `disposeInternal` by calling `deleteCompactOnDeletionCollectorFactory`.

## State and Persistence Behavior
State is a native factory handle. When attached to options, native collectors can add table properties and influence compaction behavior, but this Java wrapper stores no table data.

## Dependencies and Integration Points
It integrates with column-family/table factory options and native collector APIs.

## Risks and Test Signals
Tests should cover parameter validation, disposal, option attachment lifetime, compaction triggered by deletion ratio/window settings, and internal wrapper ownership. A risk is that `newWrapper` uses the compact-on-deletion deleter for any wrapped handle, so it must only wrap compatible native handles.
