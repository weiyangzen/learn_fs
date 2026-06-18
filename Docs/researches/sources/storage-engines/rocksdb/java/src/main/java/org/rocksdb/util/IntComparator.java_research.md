# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/util/IntComparator.java

## Purpose
`IntComparator` is a Java comparator for four-byte integer keys in ascending numeric order.

## Important APIs and Types
It extends `AbstractComparator`, implements `name()` and `compare(ByteBuffer, ByteBuffer)`, and uses private `compareIntKeys`.

## Control Flow, State, and Persistence
`compareIntKeys` reads one `int` from each buffer using relative `getInt()`, computes the difference as `long`, and clamps the result into `int` range to avoid overflow. It has no persistent state beyond inherited comparator registration.

## Dependencies and Integration Points
Depends on `AbstractComparator`, `ComparatorOptions`, and `ByteBuffer`. It can be installed on RocksDB options for integer-key databases.

## Risks and Test Signals
Keys must contain at least four bytes, and relative `getInt()` advances buffer positions. Incorrect key sizes will fail at runtime. This subset includes no direct tests for `IntComparator`.
