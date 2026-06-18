# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/util/ReverseBytewiseComparator.java

## Purpose
`ReverseBytewiseComparator` is the Java implementation of reverse bytewise ordering. It is mainly useful for testing or benchmarking because the native built-in comparator is preferred for performance.

## Important APIs and Types
It extends `AbstractComparator`, implements `name()`, `compare`, and `findShortestSeparator`. `compare` negates `BytewiseComparator._compare`.

## Control Flow, State, and Persistence
Separator shortening finds the first differing byte. For reverse order, when the start byte is greater than the limit byte and there are trailing bytes, it truncates `start` after the differing byte while preserving reverse-order invariants. It does not implement some prefix cases. There is no local persistent state.

## Dependencies and Integration Points
Depends on `AbstractComparator`, `BuiltinComparator`, `ComparatorOptions`, `Slice` docs, `ByteBuffer`, and `BytewiseComparator`. `ByteBufferUnsupportedOperationTest` installs it on a column family.

## Risks and Test Signals
Comparator callbacks mutate buffers and are slower than native comparators. Unsupported prefix shortening cases may reduce optimization but should preserve correctness. `ByteBufferUnsupportedOperationTest` stress-tests writes and iteration with this comparator, guarding against a previously intermittent unsupported operation failure.
