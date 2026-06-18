# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/ByteBufferStreamOutput.java

## Purpose
`ByteBufferStreamOutput` is an output abstraction like `OutputStream`, but centered on `ByteBuffer` writes while retaining `Closeable` and Hadoop `Syncable` behavior.

## Important APIs and Types
It declares `write(ByteBuffer, int, int)`, `flush()`, inherits `close()`, `hflush()`, and `hsync()`, and provides a default `write(ByteBuffer)` implementation using a read-only duplicate of the input buffer.

## Control Flow
The default method avoids mutating the original buffer's position or limit by writing from a read-only duplicate over its current remaining span. Concrete classes decide whether byte-buffer or byte-array writes are primary.

## State and Persistence Behavior
The interface has no state. Persistence semantics are supplied by implementors such as byte-array or byte-buffer stream output adapters and Ozone key/block output streams.

## Dependencies and Integration Points
Implemented by `ByteArrayStreamOutput` and `ByteBufferOutputStream`; used wherever Ozone output APIs need both byte-array and byte-buffer surfaces plus sync semantics.

## Risks
Implementations must define offset semantics consistently. The default `write(ByteBuffer)` passes the duplicate's current position as `off`, so implementors should treat `off` as a buffer position, not necessarily a backing-array offset.

## Test Signals
No direct test surfaced in this subset; behavior is indirectly covered by client output stream tests that exercise byte-array and byte-buffer write paths.
