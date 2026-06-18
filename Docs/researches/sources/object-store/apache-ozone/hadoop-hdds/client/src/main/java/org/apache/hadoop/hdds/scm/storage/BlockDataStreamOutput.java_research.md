# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/BlockDataStreamOutput.java

Purpose: ByteBuffer stream output for writing an Ozone block through Ratis datastream, tracking chunks, checksums, putBlock metadata, commit watches, and client cleanup.

Important APIs/types/functions: Constructor acquires a topology-aware `XceiverClientRatis`, initializes a datastream via `StreamInit`, sets up checksum and response executor, and creates `StreamCommitWatcher`. `write` fills `StreamBuffer`s, writes full buffers as datastream chunks, and triggers flush/putBlock by configured boundaries. `executePutBlock` sends metadata through both datastream close compatibility path and `putBlockAsync`. `watchForCommit`, `flush`, `hflush`, `hsync`, `close`, `cleanup`, and retry/write helpers manage lifecycle. Static `executePutBlockClose` and `getProtoLength` write close metadata over datastream.

Control flow: Writes allocate packet-sized buffers, copy incoming ByteBuffer ranges, compute chunk checksum/metadata, and call `DataStreamOutput.writeAsync`, optionally with `SYNC`. When flush boundary is reached, it updates flushed length and queues an async putBlock; when window is full, it waits for the oldest putBlock and watches the first commit index to release buffers. Close flushes remaining data, forces an EOF putBlock if needed, waits for datastream close reply, and releases the xceiver client.

State and persistence behavior: Maintains block ID, block data builder/chunk list, acquired client/factory, chunk index/offset, buffer lists, pending futures, failed servers, checksum, token string, datastream output, sync position, and exception reference. Persistent effects are datanode chunk writes and committed block metadata.

Dependencies and integration points: Integrates Ratis datastream, container protocol calls, `XceiverClientManager`, `OzoneClientConfig`, checksum code, tokens, pipelines, metrics, and commit watcher behavior.

Risks: `hsync` swallows all exceptions, which may hide failed durability operations. `dataStreamCloseReply.get()` in `close` assumes `executePutBlock(true, ...)` initialized the future. Single-thread response executor serializes completions; shutdown is not awaited. Error state is first-writer-wins, so later root causes may be suppressed. Compatibility double putBlock during close must remain aligned with datanode behavior.

Test signals: Tests should cover chunk metadata/checksum generation, flush boundaries, stream window backpressure, putBlock failure propagation, close compatibility path, sync-size `SYNC` writes, retry write path, client invalidation cleanup, and hsync error handling.
