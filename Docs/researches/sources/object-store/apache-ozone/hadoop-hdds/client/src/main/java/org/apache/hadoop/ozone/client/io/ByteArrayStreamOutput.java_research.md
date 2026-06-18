# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/ByteArrayStreamOutput.java

## Purpose
`ByteArrayStreamOutput` is an abstract adapter for output streams whose optimized primitive is `write(byte[], int, int)` but that also implement `ByteBufferStreamOutput`.

## Important APIs and Types
It implements `write(ByteBuffer, int, int)` and `write(int)`. Subclasses must provide optimized byte-array write behavior and may override byte-buffer writes. Non-array byte buffers are copied through a temporary byte array capped at 64 KiB.

## Control Flow
For array-backed buffers, the method writes the backing array directly. For non-array buffers, it repeatedly creates a read-only duplicate, positions/limits it to the current segment, copies into the reusable temporary array, and writes that array segment.

## State and Persistence Behavior
No instance state is defined. Persistence/output effects are supplied by subclass implementations.

## Dependencies and Integration Points
Implements `ByteBufferStreamOutput` and extends `OutputStream`, providing compatibility for Ozone output classes that primarily accept byte arrays.

## Risks
For array-backed buffers, the code passes `off` directly as an array offset; callers must ensure `off` matches backing-array coordinates rather than just `buffer.position()` for sliced buffers. The non-array path avoids mutating the original buffer but copies data.

## Test Signals
Indirectly covered through output stream tests that write direct/read-only `ByteBuffer`s and byte arrays.
