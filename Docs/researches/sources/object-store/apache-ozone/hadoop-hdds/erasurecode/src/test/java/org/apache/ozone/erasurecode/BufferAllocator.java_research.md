<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/BufferAllocator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/BufferAllocator.java

## Purpose
`BufferAllocator` is a test helper abstraction for allocating heap/direct ByteBuffers, optionally as slices with non-zero offsets.

## Important APIs, Types, and Functions
It defines abstract `allocate(int)`, `isUsingDirect()`, and two implementations: `SimpleBufferAllocator` and `SlicedBufferAllocator`.

## Control Flow
Simple allocation returns either `ByteBuffer.allocateDirect` or `ByteBuffer.allocate`. Sliced allocation creates a larger buffer, advances position by an offset, slices it, and limits the slice to the requested length.

## State and Persistence Behavior
Each allocator records whether it uses direct buffers. Sliced allocator also carries a slice offset. No persistent storage exists.

## Dependencies and Integration Points
It is used by `TestCoderBase` to exercise direct/heap and sliced-buffer code paths.

## Risks and Test Signals
Risks include tests missing offset-sensitive bugs if only simple allocators are used. Test signals are raw coder tests with sliced buffers and position-at-end assertions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/BufferAllocator.java -->
