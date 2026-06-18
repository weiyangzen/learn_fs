# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/util/BytewiseComparator.java

## Purpose
`BytewiseComparator` is a Java implementation of RocksDB's bytewise comparator. It exists mainly for benchmarking or specialized Java comparator use because JNI callback overhead is slower than built-in native comparators.

## Important APIs and Types
It extends `AbstractComparator`, implements `name()`, `compare(ByteBuffer, ByteBuffer)`, static `_compare`, `findShortestSeparator`, and `findShortSuccessor`.

## Control Flow, State, and Persistence
Comparison uses unsigned byte lexicographic order and falls back to length. Separator shortening finds the first differing byte, increments where safe, and truncates the `start` buffer by setting its limit. If incrementing would cross the limit, it searches for a later non-`0xff` byte. Short successor increments the first non-`0xff` byte and truncates. There is no persistent state beyond inherited native comparator registration.

## Dependencies and Integration Points
Depends on `AbstractComparator`, `ComparatorOptions`, `ByteBuffer`, `Slice` docs, and `ByteUtil.memcmp`. It integrates with options/table configuration when a Java comparator is installed.

## Risks and Test Signals
The methods mutate buffer limits and bytes, so caller-provided buffers must be writable. Absolute indexing with `remaining()` assumes callback buffers are presented from relevant zero-based slices. Built-in comparator tests cover native bytewise ordering; this Java implementation is indirectly related but not directly asserted here.
