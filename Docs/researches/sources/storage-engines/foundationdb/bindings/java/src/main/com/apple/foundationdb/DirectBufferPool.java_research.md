# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/DirectBufferPool.java

## Purpose
`DirectBufferPool` is a singleton pool of direct byte buffers used to reduce JNI range-query copy overhead when direct-buffer range queries are enabled on `FDB`.

## Important APIs, Types, And Functions
`getInstance()` returns the static singleton. `resize(int, int)` allocates a new `ArrayBlockingQueue` of direct buffers and enforces `MIN_BUFFER_SIZE`. `poll()` borrows a buffer or returns null when empty. `add(ByteBuffer)` returns a buffer only if its capacity matches the current pool generation.

## Control Flow
`FDB.resizeDirectBufferPool` calls `resize`. Range future wrappers call `poll`; on hit, JNI fills the direct buffer and a direct iterator returns it through `close`; on miss, the wrapper falls back to array-based native marshaling.

## State And Persistence Behavior
The pool keeps an in-memory queue and current buffer capacity. Resizing discards the old queue reference; outstanding old buffers are ignored when returned if their capacity no longer matches.

## Dependencies And Integration Points
It depends on Java NIO direct buffers and is used by `FutureResults`, `FutureMappedResults`, and `DirectBufferIterator`.

## Risks And Edge Cases
Large pool sizes allocate off-heap memory eagerly and can throw `OutOfMemoryError`. An empty pool is not fatal but reduces performance. Resizing during active queries intentionally drops old buffers and can temporarily reduce hit rates.

## Test Signals
Tests should cover minimum-size rejection, successful resize, pool exhaustion returning null, buffer return after resize, and range futures correctly falling back when `poll` misses.
