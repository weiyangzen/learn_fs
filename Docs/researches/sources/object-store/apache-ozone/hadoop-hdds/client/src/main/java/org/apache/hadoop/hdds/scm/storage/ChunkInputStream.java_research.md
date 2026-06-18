# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/ChunkInputStream.java

## Purpose
`ChunkInputStream` reads one container chunk and exposes it as a seekable, unbufferable, byte-buffer-readable `InputStream`. It performs partial chunk RPCs, checksum-boundary adjustment, checksum validation, and local buffer management.

## Important APIs and Types
Important APIs are `read()`, `read(byte[], int, int)`, `read(ByteBuffer)`, `seek(long)`, `getPos()`, `close()`, `unbuffer()`, `getRemaining()`, `readChunk(ChunkInfo)`, and testing accessors. It stores `ChunkInfo`, block ID, datanode block ID, `XceiverClientFactory`, client, pipeline supplier, token supplier, checksum flag, `ByteBuffer[]` cache, buffer offsets, and chunk position markers.

## Control Flow
Reads acquire a read client and call `prepareRead`. If the desired position is not in current buffers, `readChunkFromContainer` computes the actual chunk byte range. With checksum verification enabled, it expands reads to checksum boundaries, sends `ContainerProtocolCalls.readChunk`, validates response size and checksum, then caches returned read-only byte buffers. `prepareRead` returns available bytes from the active buffer, and read methods copy from that buffer to the caller. Exhausted buffers are released incrementally or entirely.

## State and Persistence Behavior
State is in-memory cache and positioning only. `bufferOffsetWrtChunkData`, `buffersSize`, `bufferOffsets`, `bufferIndex`, `firstUnreleasedBufferIndex`, and `chunkPosition` jointly define the logical read position. `unbuffer` stores the logical position, drops cached buffers, and releases the client.

## Dependencies and Integration Points
Created by `BlockInputStream`. It depends on `ContainerProtocolCalls.readChunk`, `Checksum`, `ChecksumData`, `BufferUtils`, `Pipeline`, `XceiverClientFactory`, block tokens, and Hadoop seek/unbuffer/readable interfaces.

## Risks
Positioning is delicate when checksum-boundary reads return extra bytes before the requested position. EOF and released-buffer logic must keep `getPos()` correct after buffers are nulled. If datanodes return `data` versus `dataBuffers`, both size and checksum validation paths must remain equivalent. `ByteBuffer.capacity()` is used in some seek calculations, so unexpected buffer capacity/limit relationships could be risky.

## Test Signals
`TestChunkInputStream` and `DummyChunkInputStream` cover chunk reads, seeks, checksum-boundary behavior, cached buffer state, and error paths. `TestBlockInputStream` exercises it through block-level traversal.
