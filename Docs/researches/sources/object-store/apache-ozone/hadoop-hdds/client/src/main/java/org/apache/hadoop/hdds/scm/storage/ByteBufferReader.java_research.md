# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/ByteBufferReader.java

## Purpose
`ByteBufferReader` adapts `ByteReaderStrategy` to `ByteBuffer` targets, allowing shared higher-level read loops to fill NIO buffers.

## Important APIs and Types
The constructor requires a non-null target buffer and captures its initial remaining bytes as `targetLen`. `readFromBlock(InputStream, int)` temporarily narrows the target buffer limit when the stream should read fewer bytes than the buffer has remaining, delegates to `ByteBufferReadable.read(ByteBuffer)`, restores the limit, and reduces `targetLen`. `getBuffer()` and `readImpl()` are package-visible hooks used by specialized positioned reads.

## Control Flow
The strategy asserts the underlying stream implements Hadoop `ByteBufferReadable`. This is true for `ChunkInputStream`, `ExtendedInputStream` subclasses, and the streaming block path. Limit narrowing ensures a read loop does not overrun EC cell/chunk boundaries even when the caller's buffer is larger.

## State and Persistence Behavior
State is the caller-supplied `ByteBuffer` and remaining target length. Mutations are normal buffer position advancement plus temporary limit changes. No persistence occurs.

## Dependencies and Integration Points
Used by `ExtendedInputStream.read(ByteBuffer)`, `MultipartInputStream.readFully`, `ECBlockInputStream`, and reconstructed EC stream wrappers.

## Risks
If the underlying `InputStream` is not `ByteBufferReadable`, `readImpl` fails via Ratis `Preconditions.assertInstanceOf`. Like `ByteArrayReader`, it assumes callers avoid unexpected EOF; subtracting `-1` would corrupt target length if used incorrectly.

## Test Signals
Indirectly tested through byte-buffer read variants in block, chunk, streaming, multipart, and EC stream tests.
