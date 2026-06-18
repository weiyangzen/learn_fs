# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/util/ByteUtil.java

## Purpose
`ByteUtil` contains small byte utility methods used by Java comparators.

## Important APIs and Types
`bytes(String)` returns UTF-8 bytes. `memcmp(ByteBuffer x, ByteBuffer y, int count)` compares the first `count` bytes as unsigned values and returns a signed difference like C `memcmp`.

## Control Flow, State, and Persistence
`memcmp` loops from zero to `count - 1`, using absolute `ByteBuffer.get(idx)` and masking with `0xff`. It does not alter buffer positions and has no state.

## Dependencies and Integration Points
Depends on `ByteBuffer` and `StandardCharsets.UTF_8`. `BytewiseComparator` uses `memcmp` for lexicographic ordering.

## Risks and Test Signals
`memcmp` assumes both buffers have at least `count` accessible bytes from absolute index zero, which is consistent with comparator callbacks but can be surprising if buffers have non-zero positions. Comparator behavior is indirectly validated by `BuiltinComparatorTest` for native comparators; Java comparator coverage is adjacent through `ByteBufferUnsupportedOperationTest` using `ReverseBytewiseComparator`.
