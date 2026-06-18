# sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/BlockOutputStreamEntryPool.java

Purpose: This class is the replicated key-write block manager behind `KeyOutputStream`. It owns communication with OM for block allocation, collects block location metadata for commit and hsync, maintains preallocated block entries, and shares a `BufferPool` across the underlying block streams.

Important APIs and types: The central APIs are `addPreallocateBlocks`, `allocateBlockIfNeeded`, `commitKey`, `hsyncKey`, `discardPreallocatedBlocks`, `getLocationInfoList`, `getMetadata`, and `cleanup`. It builds `BlockOutputStreamEntry` objects from `OmKeyLocationInfo`, uses `OzoneManagerProtocol.allocateBlock`, `commitKey`, `commitMultipartUploadPart`, and `hsyncKey`, and stores write context in `OmKeyArgs.Builder`, `ExcludeList`, `StreamBufferArgs`, `BufferPool`, `ContainerClientMetrics`, and `OmMultipartCommitUploadPartInfo`.

Control flow: Construction copies key identity from `OpenKeySession`, builds a shared buffer pool, and initializes an expiring exclude list. Preallocated blocks are added only for the current open version. Writes call `allocateBlockIfNeeded`, which advances past closed entries and asks OM for another block when the entry list is exhausted. Commit and hsync rebuild `OmKeyArgs` with data size, metadata, and non-empty locations; hsync avoids duplicate OM calls when the last block ID has not changed.

State and persistence behavior: Runtime state is the ordered stream-entry list, current stream index, shared buffer contents, metadata map, multipart commit result, and `lastUpdatedBlockId`. Persistent changes happen only through OM calls: allocated blocks, committed key or multipart part state, and hsync visibility. Empty stream entries are intentionally omitted from commit location metadata.

Dependencies and integration points: It integrates `KeyOutputStream`, `ECBlockOutputStreamEntryPool`, OM protocol, SCM client metrics, xceiver client factory, stream buffer settings, block tokens, pipelines, and container/pipeline exclusion used by retry handling.

Risks: The class is synchronization-sensitive around `streamEntries` and `currentStreamIndex`. `buildKeyArgs` mutates the builder by adding all metadata each time, so repeated calls rely on builder metadata semantics. Hsync deduplication by last block ID can skip OM updates when only length changes inside the same block. `discardPreallocatedBlocks` assumes unused entries have zero current position.

Test signals: Useful tests assert preallocated version filtering, allocation with exclude lists, commit location lists excluding zero-byte blocks, multipart commit info propagation, hsync error for multipart keys, hsync latency metric paths, duplicate hsync suppression, buffer cleanup, and removal of unused blocks for excluded containers or pipelines.
