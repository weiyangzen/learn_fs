# sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/MockDatanodeStorage.java

## Purpose
`MockDatanodeStorage` is an in-memory representation of one datanode's persisted container data for client unit tests. It stores block metadata, block-to-container indexes, chunk bytes, full block string data for assertions, and an optional injected failure.

## Important APIs, Types, And Functions
`setStorageFailed(IOException)` injects write failures. `putBlock` dispatches between full and incremental chunk-list updates by checking `OzoneConsts.INCREMENTAL_CHUNK_LIST` metadata. `putBlockIncremental` appends new chunks to existing block data and prunes the previous trailing partial chunk unless it is marked with `FULL_CHUNK_KV`. `putBlockFull` replaces block metadata and updates `containerBlocks`. `getBlock`, `listBlock`, `writeChunk`, `readChunkData`, `getAllBlockData`, and `getFullBlockData` provide the storage operations consumed by `MockXceiverClientSpi` and assertions.

## Control Flow
Write-chunk requests append bytes to a per-block `ByteString`, asserting that chunk offsets are sequential. Put-block requests either replace the block's chunk list or merge incremental chunk lists into an existing block. Read requests slice bytes from the stored block data according to chunk offset and length. Failure injection is checked in `writeChunk` before mutation.

## State And Persistence Behavior
All state is process-local and in-memory: `blocks`, `containerBlocks`, `fullBlockData`, `data`, and `exception`. It models persistence well enough for a single test run but has no synchronization, no deletion, and no durable storage. `fullBlockData` concatenates UTF-8 strings from written bytes and is used by EC tests to compare parity or partial-stripe content.

## Dependencies And Integration Points
It uses HDDS `BlockID`, datanode protobuf `BlockData`, `ChunkInfo`, `DatanodeBlockID`, and protobuf `ByteString`. `MockXceiverClientSpi` is the main caller, while EC and incremental put-block tests inspect the stored data directly.

## Risks And Edge Cases
The class uses Java `assert` for offset sanity, so checks can be disabled depending on JVM flags. `listBlock` assumes the container exists and will throw a null-pointer error otherwise. Incremental chunk merging has a TODO for validating offsets and lengths. `HashedMap` and ordinary `HashMap` state are not thread-safe, which can matter if async client writers interact concurrently in tests.

## Test Signals
`TestBlockOutputStreamIncrementalPutBlock` validates incremental and full chunk-list readback. `TestOzoneECClient` validates EC data/parity storage, block group length metadata, partial stripe data, retry behavior, and failure injection through this storage.
