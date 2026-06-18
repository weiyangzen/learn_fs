# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/MappedRangeResultDirectBufferIterator.java

## Purpose
`MappedRangeResultDirectBufferIterator` decodes mapped-range rows from a JNI-filled direct buffer.

## Important APIs, Types, And Functions
It extends `DirectBufferIterator` and implements `Iterator<KeyValue>` while returning `MappedKeyValue` from `next`. It reads length-prefixed key, value, range begin, range end, nested result count, and nested length-prefixed key/value pairs.

## Control Flow
After `readResultsSummary`, `MappedRangeResult` loops over this iterator. Each `next` consumes bytes from the buffer in native serialization order and increments `current`.

## State And Persistence Behavior
The cursor is the inherited buffer position plus `current` count. Close returns the direct buffer to the pool.

## Dependencies And Integration Points
It depends on `DirectBufferIterator`, `MappedKeyValue`, and `KeyValue`, and is used by `FutureMappedResults.getResults`.

## Risks And Edge Cases
The iterator declares `Iterator<KeyValue>` but returns `MappedKeyValue`, relying on covariance. It uses a raw `ArrayList` without generic parameter. Malformed buffer lengths can underflow or throw.

## Test Signals
Tests should decode rows with zero and multiple nested results, verify `NoSuchElementException`, malformed buffer handling, and buffer return through close.
