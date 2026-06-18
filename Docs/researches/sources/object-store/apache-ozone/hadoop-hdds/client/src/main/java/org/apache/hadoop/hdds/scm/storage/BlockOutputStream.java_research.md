# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/BlockOutputStream.java

## Purpose
`BlockOutputStream` is the core buffered writer for writing one Ozone block to container datanodes. It batches user writes into `ChunkBuffer`s, emits `WriteChunk` requests, periodically emits `PutBlock`, tracks asynchronous responses, and coordinates retry, flush, close, checksum, and client cleanup semantics. `RatisBlockOutputStream` and `ECBlockOutputStream` specialize commit behavior.

## Important APIs and Types
Key public APIs are `write(int)`, `write(byte[], int, int)`, `flush()`, `close()`, `waitForAllPendingFlushes()`, `writeOnRetry(long)`, `cleanup(boolean)`, and getters for block ID, buffer pool, failed servers, flushed length, and written length. Important extension hooks include `executePutBlock(boolean, boolean)`, `sendWatchForCommit(long)`, `updateCommitInfo(...)`, `waitOnFlushFuture()`, `releaseBuffersOnException()`, and `cleanup()`. `PutBlockResult` carries commit index and response.

## Control Flow
Writes allocate from `BufferPool`, copy bytes into `currentBuffer`, update `writtenDataLength`, and call `writeChunkIfNeeded()` when the buffer fills. Full buffers are sent using `writeChunkToContainer`, which computes checksum, creates `ChunkInfo`, validates monotonic offsets, updates `containerBlockData`, and sends async RPCs. `doFlushOrWatchIfNeeded()` emits `PutBlock` every flush period and records a future chain that waits for commit. `flush` and `close` call `handleFlushInternalSynchronized`, which flushes partial buffers, commits uncommitted chunks, or sends a forced EOF `PutBlock` on close. Piggybacking can combine `WriteChunk` and `PutBlock` when datanode versions support it.

## State and Persistence Behavior
The stream tracks the current block ID and BCSID, planned block size, EOF flag, previous chunk, chunk index/offset, buffer pool state, asynchronous IO exception, total write/put lengths, pending buffer list, checksum state, token string, replication index, and pending flush futures. Persistent effects are container chunk writes and committed block metadata. Incremental chunk-list mode keeps only newly sent chunks in `PutBlock` and uses a direct `lastChunkBuffer` to maintain partial chunk checksum state.

## Dependencies and Integration Points
It integrates with `ContainerProtocolCalls.writeChunkAsync` and `putBlockAsync`, `XceiverClientFactory`, `XceiverClientSpi`, `ContainerClientMetrics`, `Checksum`, `ChunkBuffer`, `DirectBufferPool`, `StreamBufferArgs`, and datanode version feature gates. `RatisBlockOutputStream` supplies commit watching and buffer release; `ECBlockOutputStream` changes putBlock semantics for EC metadata and does not use Ratis commit watching.

## Risks
Most risk is in asynchronous ordering and resource release. `ioException` causes later operations to fail with the original error, but futures may complete concurrently. `bufferList` is handed off to putBlock handling and must not be reused incorrectly. Incremental chunk-list checksum maintenance depends on exact partial/full chunk offset handling and `lastChunkBuffer` lifecycle. Interrupt handling wraps errors as `IOException`; callers relying on thread interrupt state should check it. Version-gated piggybacking must remain aligned with datanode compatibility.

## Test Signals
`TestBlockOutputStreamCorrectness` covers Ratis/EC chunk and putBlock correctness, checksum-related behavior, and stream construction. Buffer release and blocking assumptions are supported by `TestBufferPool`; integration behavior is also exercised by broader Ozone client write tests.
