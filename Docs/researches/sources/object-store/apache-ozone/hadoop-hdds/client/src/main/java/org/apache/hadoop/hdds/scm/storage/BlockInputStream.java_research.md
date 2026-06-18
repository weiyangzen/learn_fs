# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/BlockInputStream.java

## Purpose
`BlockInputStream` is the non-streaming, block-level read implementation used by higher key streams to read one Ozone block from container datanodes. It lazily retrieves block metadata, builds one `ChunkInputStream` per chunk, and then presents those chunks as one seekable `BlockExtendedInputStream`.

## Important APIs and Types
The main constructor accepts `BlockLocationInfo`, `Pipeline`, block token, `XceiverClientFactory`, refresh callback, and `OzoneClientConfig`. Public APIs include `initialize()`, `readWithStrategy(ByteReaderStrategy)`, `seek(long)`, `getPos()`, `close()`, `unbuffer()`, `getBlockID()`, `getLength()`, and testing accessors for chunk state. `getBlockData()` and `getBlockDataUsingClient()` perform the container `getBlock` RPC. `createChunkInputStream()` is a protected factory hook used by tests and subclasses.

## Control Flow
Reads first call `initialize()` if needed. Initialization acquires a read client, invokes `ContainerProtocolCalls.getBlock`, validates chunk lengths, updates under-construction length from datanode block data, computes `chunkOffsets`, and constructs lazy chunk streams. `readWithStrategy` loops over the active chunk, caps each request by chunk remaining bytes, delegates to `ByteArrayReader` or `ByteBufferReader`, advances `chunkIndex`, and requires exact reads from each chunk. `seek` either stores a pre-initialization block position or binary-searches `chunkOffsets`, resets prior/future chunks, and seeks the selected chunk.

## State and Persistence Behavior
State is in-memory only: `pipelineRef`, `tokenRef`, `xceiverClient`, `chunkStreams`, `chunkOffsets`, `chunkIndex`, `blockPosition`, retry count, and cached `blockData`. The class does not persist data; it reflects persisted container metadata returned by datanodes. `close` releases the read client and closes chunk streams; `unbuffer` stores position and releases clients/buffers without closing the logical stream.

## Dependencies and Integration Points
It depends on `BlockExtendedInputStream` retry helpers, `ContainerProtocolCalls`, `XceiverClientFactory`, `Pipeline`, `BlockLocationInfo`, `ChunkInputStream`, block tokens, and Ozone checksum config. `BlockInputStreamFactoryImpl` creates this for non-EC reads when streaming read is unavailable or disabled. `MultipartInputStream` can aggregate it as a `PartInputStream`.

## Risks
The implementation assumes chunk metadata is ordered and lengths are accurate; inconsistent chunk EOFs are treated as corruption. Retry behavior depends on distinguishing storage/security/connectivity exceptions and on the refresh callback returning usable block location data. Seek state is subtle because pre-initialization `blockPosition`, `chunkIndexOfPrevPosition`, and chunk-local positions must remain coherent. The validator deliberately tolerates a last zero-length EC chunk at block length for HDDS-10682, so future validation changes must preserve that compatibility.

## Test Signals
`TestBlockInputStream`, `DummyBlockInputStream`, and `DummyBlockInputStreamWithRetry` exercise initialization, seek/read behavior, retry/refresh paths, and mocked chunk failures. `TestChunkInputStream` indirectly validates chunk-level behavior used here.
