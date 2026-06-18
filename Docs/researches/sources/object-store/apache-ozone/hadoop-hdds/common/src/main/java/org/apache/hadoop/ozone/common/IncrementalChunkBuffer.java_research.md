# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/IncrementalChunkBuffer.java

## Purpose

`IncrementalChunkBuffer` implements a logical fixed-limit `ChunkBuffer` backed by direct `CodecBuffer`s allocated only as data is written. This reduces memory pressure for large chunk capacities when producers may not fill the whole buffer.

## APIs and control flow

Construction records the logical limit, increment size, last index, buffer list, and release list. `getAndAllocateAtIndex` allocates direct buffers up to the requested component. `position()` finds the first non-full buffer and asserts that later allocated buffers remain empty. `put(ByteBuffer)` checks overflow, then writes across increment-sized components, temporarily narrowing the source buffer limit. `duplicate(newPosition, newLimit)` creates a read-only-style duplicated `IncrementalChunkBuffer` containing duplicates of already allocated buffers over the requested range. `iterate(bufferSize)` only supports a buffer size equal to the increment and returns the backing list. `close()` releases all owned `CodecBuffer`s.

## State, dependencies, and integration

Mutable state includes allocated buffers, underlying direct buffers, and `firstNonFullIndex`. Duplicated instances have no owned underlying buffers and reject allocation. The class depends on Guava preconditions, HDDS `CodecBuffer`, `BufferUtils`, and Ratis `ByteString`. It is selected by `ChunkBuffer.allocate(capacity, increment)`.

## Risks and test signals

The code assumes sequential writes: full buffers, one partially filled buffer, then empty/unallocated buffers. Random external mutation through `asByteBufferList()` can violate invariants. Duplicate ranges require all referenced buffers to already exist. Tests should cover incremental allocation count, boundary capacities, full-capacity writes, overflow, close release, duplicate across increments, unsupported iteration sizes, and position invariants after rewind/clear.
