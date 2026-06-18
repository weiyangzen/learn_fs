# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractComparator.java

## Purpose
This Java abstract base class lets users implement RocksDB key comparators in Java. It keeps the public comparator API focused while native callback plumbing is handled by other bridge classes.

## Important APIs, Types, and Functions
The class extends `RocksCallbackObject`. It provides constructors, `initializeNative`, package-private `getComparatorType`, abstract `name`, abstract `compare(ByteBuffer a, ByteBuffer b)`, optional `findShortestSeparator`, optional `findShortSuccessor`, `usingDirectBuffers`, and native methods `usingDirectBuffers(long)` and `createNewComparator(long)`.

## Control Flow
Subclasses define a total order in `compare` and optionally shorten separator/successor keys by mutating byte buffer position/limit semantics. Initialization creates a native comparator wrapper using `ComparatorOptions`. Native code calls through `AbstractComparatorJniBridge` for callback dispatch.

## State and Persistence Behavior
The comparator's native handle is callback state. Comparator behavior affects persistent SST ordering and DB compatibility. The `name` contract is critical because RocksDB uses it to detect comparator mismatch when reopening DBs.

## Dependencies and Integration Points
It integrates with `ComparatorOptions`, `ComparatorType`, `RocksCallbackObject`, `AbstractComparatorJniBridge`, and native comparator callback code. `WriteBatchWithIndex` can also accept Java comparator handles for fallback index comparison.

## Risks and Edge Cases
A comparator must define a stable total order; changing comparator semantics without changing `name` can corrupt or make existing DBs unreadable. ByteBuffer mutation is allowed only within documented bounds. Direct-buffer support depends on native wrapper configuration. The package-private default constructor restricts uncontrolled use.

## Test Signals
Tests should cover comparator ordering, DB reopen mismatch detection through names, separator/successor mutation behavior, direct versus indirect buffer configuration, and integration with `WriteBatchWithIndex` fallback comparators.
