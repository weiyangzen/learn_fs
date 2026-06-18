# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/DirectBufferIterator.java

## Purpose
`DirectBufferIterator` is the shared base for iterating JNI-filled direct `ByteBuffer` range-query result chunks without first marshaling the entire payload through regular Java arrays.

## Important APIs, Types, And Functions
It stores `byteBuffer`, `current`, `keyCount`, and `more`. `readResultsSummary()` rewinds the buffer and reads native-endian `keyCount` and `more`; `hasNext`, `count`, `hasMore`, and `currentIndex` expose parsed state. `close()` returns the buffer to `DirectBufferPool`.

## Control Flow
`FutureResults.getResults()` or `FutureMappedResults.getResults()` borrows a buffer, calls a native direct-fill function, then creates a concrete direct-buffer iterator. The subclass reads items after `readResultsSummary`.

## State And Persistence Behavior
The iterator owns one borrowed direct buffer until `close`. Parsed cursor state is mutable and in-memory. Closing returns reusable buffers to the singleton pool and nulls the local reference.

## Dependencies And Integration Points
It depends on `ByteBuffer`, `ByteOrder.nativeOrder`, `DirectBufferPool`, and concrete `RangeResultDirectBufferIterator` / `MappedRangeResultDirectBufferIterator`.

## Risks And Edge Cases
Callers must call `readResultsSummary` before `hasNext`, `count`, or `hasMore`. Buffer format must match JNI exactly. Returning a buffer while still reading would corrupt results, so the try-with-resources conversion must finish before close.

## Test Signals
Tests should feed native-order buffers with empty and multi-row chunks, verify `more` parsing, assert close returns buffers to the pool, and exercise misuse before summary parsing under assertions.
