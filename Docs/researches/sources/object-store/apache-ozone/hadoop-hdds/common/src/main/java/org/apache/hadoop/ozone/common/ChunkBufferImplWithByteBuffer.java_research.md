# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/ChunkBufferImplWithByteBuffer.java

## Purpose

This package-private `ChunkBuffer` implementation wraps a single `ByteBuffer`. It is the simplest backing strategy and is used when a full chunk buffer is allocated up front or when an existing single buffer is adapted.

## APIs and control flow

The implementation delegates `position`, `remaining`, `limit`, `rewind`, `clear`, `put`, equality, and hash code to the wrapped `ByteBuffer`. `iterate(bufferSize)` returns duplicated slices from the current position to the limit, advancing the original buffer by the emitted slice size. `duplicate(newPosition, newLimit)` returns a new wrapper over a duplicated `ByteBuffer`. `writeTo` drains the buffer through `BufferUtils.writeFully`.

## State, dependencies, and integration

State is the mutable `ByteBuffer` plus an optional `UncheckedAutoCloseable` `underlying`, normally the direct `CodecBuffer` allocated by `ChunkBuffer.allocate`. `close()` releases only when that underlying resource exists. ByteString conversion passes the live buffer through the supplied converter, relying on `ChunkBufferToByteString` to enforce position and limit preservation.

## Risks and test signals

Because `asByteBufferList()` exposes the live buffer, callers can mutate position and limit outside the wrapper. Iteration is destructive with respect to position. Tests should check that close releases direct buffers once, iteration chunking is correct, duplicate views have independent positions, and conversion functions do not disturb the underlying buffer.
