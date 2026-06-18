## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/BlockDataStreamOutputEntryPool.java

### Purpose
`BlockDataStreamOutputEntryPool` manages the list of byte-buffer block stream entries for a key write, handles preallocated and newly allocated blocks, tracks metadata, commits or hsyncs keys with OM, and manages excluded pipelines/nodes after failures.

### Important APIs and Types
State includes `streamEntries`, config, current stream index, `OzoneManagerProtocol`, `OmKeyArgs.Builder`, metadata map, `XceiverClientFactory`, multipart commit info, open ID, `ExcludeList`, shared buffer list, and `lastUpdatedBlockId`. Important methods include `addPreallocateBlocks`, `getLocationInfoList`, `hsyncKey`, `discardPreallocatedBlocks`, `allocateBlockIfNeeded`, `commitKey`, `cleanup`, `computeBufferData`, `getDataSize`, and `getMetadata`.

### Control Flow
Construction seeds `OmKeyArgs.Builder` from the open key info and multipart parameters. `addPreallocateBlocks` filters an `OmKeyLocationInfoGroup` to blocks for the current open version before creating stream entries. `allocateBlockIfNeeded` advances past closed entries, calls OM `allocateBlock` when entries are exhausted, and returns the current entry. `getLocationInfoList` converts non-empty stream entries into OM location info for commit. `hsyncKey` updates data size and locations, rejects multipart hsync, and calls OM only when no locations exist or the last block ID changed since the previous hsync. `commitKey` verifies caller offset equals accumulated length, populates key args, and commits either a multipart upload part or a normal key.

### State and Persistence Behavior
The pool is stateful for one open key. It tracks which block entry is current, accumulated metadata, buffered data, excluded nodes, and last hsynced block. Persistent effects occur through OM calls: allocate block, hsync key, commit key, or commit multipart upload part. `cleanup` clears local entries and exclude list but does not itself abort OM state.

### Dependencies and Integration Points
It integrates with `OzoneManagerProtocol`, `OmKeyArgs`, `OmKeyInfo`, `OmKeyLocationInfo`, `OmKeyLocationInfoGroup`, `OmMultipartCommitUploadPartInfo`, `ExcludeList`, `PipelineID`, `StreamBuffer`, and `BlockDataStreamOutputEntry`.

### Risks and Edge Cases
`buildKeyArgs` adds all metadata to the builder on every call; repeated calls rely on builder behavior to avoid unintended duplication/overwrites. `hsyncKey` only sends updates when the last block ID changes, so appended data within the same block may not trigger another hsync. `discardPreallocatedBlocks` asserts unused blocks have position zero. `commitKey` requires offset exactly equal to local length and will fail fast on mismatch.

### Test Signals
Tests should cover preallocated block filtering by open version, allocation when current entry is closed or absent, non-empty location reporting only, multipart hsync rejection, hsync suppression/reissue based on last block ID, commit normal vs multipart behavior, discard of unused blocks by pipeline/container, metadata propagation, and cleanup clearing local state.
