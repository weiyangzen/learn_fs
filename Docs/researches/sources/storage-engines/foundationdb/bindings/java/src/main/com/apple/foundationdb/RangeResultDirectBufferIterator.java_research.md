# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/RangeResultDirectBufferIterator.java

## Purpose
`RangeResultDirectBufferIterator` decodes standard range-query key/value rows from a direct buffer filled by JNI.

## Important APIs, Types, And Functions
It extends `DirectBufferIterator` and implements `Iterator<KeyValue>`. `next` reads key length, value length, key bytes, and value bytes from the current buffer position, increments `current`, and returns a `KeyValue`.

## Control Flow
`RangeResult` calls `readResultsSummary`, then repeatedly calls `next` for the parsed count.

## State And Persistence Behavior
State is inherited buffer cursor and row index. Closing returns the direct buffer to `DirectBufferPool`.

## Dependencies And Integration Points
It is used by `FutureResults.getResults` and depends on `KeyValue`.

## Risks And Edge Cases
Malformed or undersized buffers throw `BufferUnderflowException` or allocate bad sizes. `next` requires summary parsing first.

## Test Signals
Tests should cover single and multi-row decoding, empty result behavior, `NoSuchElementException`, and buffer return on close.
