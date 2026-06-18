# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/AbstractComparatorJniBridge.java

## Purpose
This package-private bridge class contains private static methods invoked from JNI to call Java `AbstractComparator` methods while preserving public API cleanliness and ByteBuffer bounds.

## Important APIs, Types, and Functions
Private JNI-called methods are `compareInternal`, `findShortestSeparatorInternal`, and `findShortSuccessorInternal`. They accept an `AbstractComparator`, one or two `ByteBuffer`s, and native-provided lengths.

## Control Flow
`compareInternal` marks and limits each buffer when a length is provided, calls `comparator.compare`, resets marked buffers, and returns the comparison result. Separator/successor methods set buffer limits, call the corresponding comparator method, and return the remaining byte count, which native code interprets as the new key length.

## State and Persistence Behavior
The bridge mutates ByteBuffer position/limit state temporarily or intentionally for key shortening. It does not persist data, but comparator decisions affect RocksDB ordering and persisted SST structure.

## Dependencies and Integration Points
It is used by native comparator JNI callback code and interacts with `AbstractComparator`. SpotBugs/PMD suppressions are necessary because methods are private and only invoked by native code.

## Risks and Edge Cases
`compareInternal` uses `mark`/`reset` only when length is provided; comparator implementations that modify position can affect reset semantics if they alter marks unexpectedly. Separator/successor methods do not restore limits because the remaining length is the output contract. Invalid native lengths can cause `IllegalArgumentException` from ByteBuffer limit changes.

## Test Signals
Tests should call comparators through native RocksDB paths and verify correct bounds, no buffer aliasing between inputs, separator/successor output length handling, and exception propagation for invalid comparator behavior.
