# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/StreamBlockInputStream.java

## Purpose
`StreamBlockInputStream` reads an entire block through the newer streaming gRPC read-block protocol rather than issuing per-chunk read RPCs. It supports normal reads, byte-buffer reads, seek, unbuffer, pre-read, response queueing, checksum verification, timeouts, and pipeline refresh on retryable errors.

## Important APIs and Types
Public APIs include `read()`, `read(byte[], int, int)`, `read(ByteBuffer)`, package `readFully(ByteBuffer, boolean)`, `seek`, `getPos`, `unbuffer`, `close`, and config getters for pre-read size, response data size, and timeout. The nested `StreamingReader` implements `StreamingReaderSpi` and handles gRPC observer callbacks.

## Control Flow
Reads call `dataAvailableToRead`, which initializes a `StreamingReader` and client stream if needed, then requests enough data through `readBlock`. `requestedLength` tracks bytes already requested from the server and may include configured pre-read. Responses are queued by `StreamingReader.onNext`, verified by checksum if enabled, and drained by `readFromQueue`, which adjusts for checksum-boundary offsets before returning a read-only `ByteBuffer`. `advancePosition` closes the stream at block EOF. `seek` closes the current stream, updates logical position, and sets `requestedLength` to the seek position.

## State and Persistence Behavior
State includes block ID/length, response sizing, pre-read settings, timeout, pipeline/token refs, client, current buffer, position, requested length, streaming reader, retry count, and refresh callback. It does not persist data; it consumes persisted block bytes from datanodes. Closing/unbuffering releases client resources and completes/cancels gRPC streams.

## Dependencies and Integration Points
Created by `BlockInputStreamFactoryImpl` when config enables stream reads and all datanodes support `STREAM_BLOCK_SUPPORT`. It uses `XceiverClientGrpc`, `StreamingReadResponse`, `ContainerProtocolCalls.buildReadBlockCommandProto`, `Checksum`, and block-location refresh helpers.

## Risks
Timeout and queue completion logic is critical: `poll` checks queue emptiness before `future.isDone()` to avoid dropping a response delivered just before completion. `readFromQueue` assumes `poll()` returns a non-null item; unexpected stream completion without data could cause null handling issues. Seek/close races are guarded by synchronization, but gRPC callbacks can arrive asynchronously. Checksum failure attempts to call request observer `onError` and release stream resources.

## Test Signals
`TestStreamBlockInputStream` covers custom configuration, stream close/cancel behavior, timeout/queue behavior, checksum and observer paths, and resource release. `BlockInputStreamFactoryImpl` tests cover selection of this class.
