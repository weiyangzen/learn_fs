# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/BufferPool.java

## Purpose
`BufferPool` is a bounded, blocking pool of reusable `ChunkBuffer` instances for block writes. It prevents unbounded client memory usage by limiting concurrently allocated buffers and reusing released buffers.

## Important APIs and Types
Primary APIs are `allocateBuffer(int)`, `releaseBuffer(ChunkBuffer)`, `waitUntilAvailable()`, `clearBufferPool()`, `computeBufferData()`, `getAllocatedBuffers()`, `getNumberOfUsedBuffers()`, `isAtCapacity()`, and size/capacity getters. `empty()` returns a static zero-capacity pool used by some tests and EC code paths. The pool also exposes a `byteStringConversion()` strategy for turning `ByteBuffer`s into Ratis `ByteString`s.

## Control Flow
`allocateBuffer` takes an interruptible lock, asserts total created buffers do not exceed capacity, waits on `notFull` while allocated size equals capacity, then reuses a released buffer or allocates a new `ChunkBuffer`. `releaseBuffer` removes the exact object identity from the allocated list, clears it, appends it to the released list, clears `currentBuffer` if needed, and signals one waiter.

## State and Persistence Behavior
All state is in memory: buffer size, capacity, allocated list, released list, current buffer, lock, and condition. No data is persisted. `clearBufferPool` closes all tracked buffers and resets lists.

## Dependencies and Integration Points
`BlockOutputStream` allocates buffers for user writes and `CommitWatcher` releases them after commit. The pool uses `ChunkBuffer`, Ratis `Preconditions`, and `ByteStringConversion`.

## Risks
Callers must release only buffers obtained from this pool; identity-based removal intentionally rejects equivalent but different objects. Capacity zero pools cannot allocate without waiting forever, so they are only safe in paths that do not call allocation. Interruptions during allocation propagate through block stream error handling. Incorrect commit watcher behavior can starve writers blocked on `notFull`.

## Test Signals
`TestBufferPool` covers allocation, release, capacity blocking, concurrent waits, reallocation, empty state, and pool accounting.
