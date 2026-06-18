# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/ChunkBufferImplWithByteBufferList.java

## Purpose

`ChunkBufferImplWithByteBufferList` adapts multiple `ByteBuffer` instances into one logical `ChunkBuffer`. It supports chunk data that is already segmented, avoiding an immediate copy into a single contiguous buffer. The class is explicitly not thread-safe.

## APIs and control flow

Construction stores an immutable copy of the buffer list, substitutes a zero-length buffer for an empty list, computes total logical limit from component limits, and finds the current component by scanning positions. `put(ByteBuffer)` checks logical remaining capacity and writes across component boundaries. `duplicate(newPosition, newLimit)` creates per-buffer duplicates whose positions and limits are clipped to the requested logical range. `iterate(bufferSize)` returns a duplicate of the current component when possible, otherwise allocates a temporary buffer to bridge multiple components. `writeTo` drains the list via gathering writes and then rescans current state.

## State, dependencies, and integration

State is the immutable list of mutable component buffers, total logical limit, `currentIndex`, and `limitPrecedingCurrent`. It depends on Guava preconditions/immutable lists, `BufferUtils`, and Ratis `ByteString`. It integrates with reads or network paths that naturally produce multiple buffers.

## Risks and test signals

The implementation temporarily changes source buffer limits while copying across components in `put` and `iterate`; incorrect reset or external mutation can corrupt later positions. `asByteBufferList()` exposes live buffers. Tests should cover empty lists, current detection invariants, cross-buffer writes, range duplication at component boundaries, gathering write position updates, and iteration when requested size spans buffers.
