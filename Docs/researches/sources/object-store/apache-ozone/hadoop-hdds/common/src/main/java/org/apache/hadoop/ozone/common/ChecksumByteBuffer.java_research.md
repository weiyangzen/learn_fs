# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/ChecksumByteBuffer.java

## Purpose
`ChecksumByteBuffer` extends `java.util.zip.Checksum` with an explicit `update(ByteBuffer)` method while maintaining Java 8 compatibility.

## Important APIs, types, and functions
- `void update(ByteBuffer buffer)` updates checksum state from the buffer and advances position to limit.
- Default `update(byte[] b, int off, int len)` wraps the byte range as a read-only `ByteBuffer` and delegates to `update(ByteBuffer)`.

## Control flow
Implementations provide ByteBuffer update behavior. The byte-array default path centralizes update logic through ByteBuffer handling.

## State and persistence behavior
The interface has no state. Implementations maintain checksum accumulator state and expose it through inherited `getValue`/`reset`.

## Dependencies and integration points
It integrates `java.util.zip.Checksum` implementations with Ozone checksum calculation, especially direct/read-only buffer support in `ChecksumByteBufferImpl`.

## Risks and edge cases
The missing `@Override` on `update(ByteBuffer)` is intentional for Java 8 compatibility because the JDK interface added that method later. Implementations must obey the position-advancing contract, or checksum slicing logic can break.

## Test signals
Tests should verify byte-array and ByteBuffer updates produce identical CRC values, buffer positions advance to limit, read-only buffers work, and reset/getValue semantics match `Checksum`.
