# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/util/BufferUtil.java

## Purpose
`BufferUtil` provides a compact bounds-check helper for offset/length/size validation.

## Important APIs and Types
`CheckBounds(int offset, int len, int size)` throws `IndexOutOfBoundsException` if any component is negative or if `offset + len` exceeds `size`.

## Control Flow, State, and Persistence
The method uses a bitwise aggregate check: `(offset | len | (offset + len) | (size - (offset + len))) < 0`. There is no state or persistence.

## Dependencies and Integration Points
It depends only on `String.format`/JDK exceptions and is intended for buffer-oriented JNI wrapper methods.

## Risks and Test Signals
The compact check relies on two's-complement overflow behavior; very large `offset + len` overflow is intentionally caught as negative. No direct tests for this helper are in the subset, though ByteBuffer transaction tests cover adjacent buffer behavior.
