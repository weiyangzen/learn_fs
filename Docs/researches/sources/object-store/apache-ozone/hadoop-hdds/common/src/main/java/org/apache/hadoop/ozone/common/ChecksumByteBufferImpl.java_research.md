# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/ChecksumByteBufferImpl.java

## Purpose
`ChecksumByteBufferImpl` adapts any `java.util.zip.Checksum` implementation to the Ozone `ChecksumByteBuffer` interface, adding efficient `ByteBuffer` update support across Java 8 and Java 9+.

## Important APIs, types, and functions
- Constructor stores the wrapped `Checksum`.
- Static initialization resolves Java 8 private `ByteBuffer.isReadOnly` field for a no-copy array path and Java 9+ `Checksum.update(ByteBuffer)` method handle for native ByteBuffer updates.
- `update(ByteBuffer buffer)` prefers Java 9+ `Checksum.update(ByteBuffer)`, otherwise tries to clear read-only state reflectively and update from backing array when present, falling back to copying remaining bytes into an array.
- `update(byte[]...)`, `update(int)`, `getValue()`, and `reset()` delegate to the wrapped checksum.

## Control flow
On Java 9+, `BYTE_BUFFER_UPDATE.invokeExact` is the primary path and advances the buffer per JDK behavior. On Java 8, reflection may allow `hasArray()` on read-only heap buffers, avoiding a copy; otherwise the method copies remaining bytes and updates the checksum.

## State and persistence behavior
Instances hold mutable checksum accumulator state in the wrapped `Checksum`. Static method handles/field references are process-wide. No persistence exists.

## Dependencies and integration points
It depends on `JavaUtils`, reflection, method handles, `ByteBuffer`, `Checksum`, and SLF4J. It is created by `ChecksumByteBufferFactory` and used by `Checksum`.

## Risks and edge cases
- Reflectively mutating `ByteBuffer.isReadOnly` on Java 8 is fragile and can violate buffer immutability expectations.
- In the Java 8 array-backed path, the code calls `checksum.update` but does not advance the buffer position, despite the interface contract saying position should reach limit. The copy path does advance because `buffer.get(b)` is used. Callers should not rely on position after array-backed Java 8 updates unless tests confirm behavior.
- Method-handle invocation wraps any failure as `IllegalStateException`.
- The class is not thread-safe unless the wrapped checksum is externally synchronized.

## Test signals
Tests should cover heap, read-only heap, direct, and sliced buffers; Java 8 and Java 9+ behavior; position advancement; values matching reference CRC implementations; reset; and error behavior if reflection/method handles are unavailable.
