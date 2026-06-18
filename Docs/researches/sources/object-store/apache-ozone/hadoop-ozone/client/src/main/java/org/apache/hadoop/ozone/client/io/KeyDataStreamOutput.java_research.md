# sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/KeyDataStreamOutput.java

Purpose: This output stream writes keys from `ByteBuffer` inputs through `BlockDataStreamOutputEntryPool`. It is the data-stream counterpart to `KeyOutputStream`, using SCM byte-buffer stream abstractions while preserving OM allocation, retry, hsync, and commit semantics.

Important APIs and types: Main methods are `write(ByteBuffer,int,int)`, `addPreallocateBlocks`, `flush`, `hsync`, `hflush`, `close`, `setPreCommits`, `getCommitUploadPartInfo`, `getMetadata`, and test accessors for entries, locations, xceiver manager, client ID, and exclude list. It uses `AbstractDataStreamOutput`, `BlockDataStreamOutputEntry`, `BlockDataStreamOutputEntryPool`, `BlockDataStreamOutput`, `OzoneClientConfig`, `ExcludeList`, and OM helper types.

Control flow: Construction builds an entry pool from the open key session and retry policy. Writes allocate a current block, write as much as fits, close full blocks, and update logical offsets. On IOException it determines retry/container exclusion, updates acked position, optionally issues putBlock/watchForCommit, excludes failed datanodes/pipelines/containers, cleans the failed stream, discards invalid preallocations, and rewrites buffered data through retry. Flush, hsync, full-block close, and close all dispatch through `handleFlushOrClose`.

State and persistence behavior: Runtime state includes closed flag, offset, writeOffset, client ID, pre-commit hooks, and the entry pool. Persistent state is datanode chunk/block metadata plus OM key or multipart-part commit state. Hsync updates OM visibility at `writeOffset` after the data stream hsync succeeds.

Dependencies and integration points: Used by `OzoneDataStreamOutput` for byte-buffer writes and by `ClientProtocol.createStreamKey`/file stream APIs. It integrates SCM data-stream output, retry policy from `HddsClientUtils`, block preallocation, OM commit, and key metadata propagation.

Risks: The class comments say multi-thread access is not supported, unlike `KeyOutputStream` which has explicit lock/semaphore logic. Exception handling has subtle offset and buffered-data invariants. `chunkSize` is passed in the constructor but not used directly here, so behavior depends on the entry pool. Closing after exception skips offset equality checks.

Test signals: Tests should cover ByteBuffer offset/length writes across block boundaries, hsync position checks, retry after partial writes, exclude-list updates, full-block close, pre-commit ordering, multipart info return, metadata propagation, and cleanup on failed close.
