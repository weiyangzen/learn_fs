## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/interfaces/ChunkManager.java

Purpose: Defines the chunk-level data contract for key-value containers, covering chunk write/read/delete, bulk delete, streaming setup, write finalization hooks, and read-buffer sizing.

Important APIs and functions: `writeChunk()` accepts `ChunkBuffer` and has a default `ByteBuffer` wrapper. `readChunk()` returns `ChunkBufferToByteString`. `deleteChunk()` and `deleteChunks()` remove chunk files. `finishWriteChunks()`, `finalizeWriteChunk()`, `streamInit()`, and `getStreamDataChannel()` are optional hooks for layouts that support streaming. `getBufferCapacityForChunkRead()` computes read buffer capacity from chunk flags and checksum data.

Control flow and state: The interface is stateless, with no-op defaults for optional lifecycle hooks. Buffer sizing prefers single-buffer reads for old clients, checksum-boundary buffers for checksummed reads, configured defaults for checksum type NONE, and chunk length as fallback.

Persistence and dependencies: Implementations touch container chunk files and may update metadata through `BlockData`. It integrates with `Container`, `KeyValueContainer`, `BlockID`, `ChunkInfo`, `ContainerMetrics`, `DispatcherContext`, Ratis `StateMachine.DataChannel`, checksum metadata, and Ozone buffer wrappers.

Risks: Partial read/write support is explicitly incomplete. Buffer capacity can overflow `int`, and the helper throws on overflow. Optional stream methods returning null require callers to guard by implementation capability. Chunk deletion must remain consistent with block metadata deletion.

Test signals: Cover write/read/delete for file-per-block and file-per-chunk layouts, ByteBuffer wrapper behavior, checksum NONE and non-NONE buffer sizing, old-client single-buffer reads, integer overflow, streaming init/data-channel support, and no-op default finalization paths.
