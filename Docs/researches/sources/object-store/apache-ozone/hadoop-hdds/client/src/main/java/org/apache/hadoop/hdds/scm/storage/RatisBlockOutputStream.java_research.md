# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/RatisBlockOutputStream.java

## Purpose
`RatisBlockOutputStream` is the Ratis-specific block writer. It adds commit-index watching and `Syncable` flush semantics to `BlockOutputStream`.

## Important APIs and Types
The constructor builds the base stream and a `CommitWatcher`. Overrides include `getTotalAckDataLength`, `releaseBuffersOnException`, `sendWatchForCommit`, `updateCommitInfo`, `waitOnFlushFuture`, `cleanup`, `hflush`, and `hsync`. `getCommitIndex2flushedDataMap` is visible for tests.

## Control Flow
After base writes/putBlocks produce Ratis log indexes, this class maps those log indexes to the buffers flushed in that commit. `sendWatchForCommit` asynchronously waits for replication. When complete, `CommitWatcher` releases buffers and updates acknowledged length. `hsync`/`hflush` call base `handleFlush(false)` while the stream is open.

## State and Persistence Behavior
Ratis-specific state lives in `CommitWatcher`: commit-index maps and ack length. Persistent data effects are inherited from base write/putBlock RPCs; this class controls when local buffers can be reused.

## Dependencies and Integration Points
Used for RATIS replication write paths. It depends on `CommitWatcher`, `BufferPool`, `XceiverClientReply`, Hadoop `Syncable`, and the base block stream asynchronous flush pipeline.

## Risks
Correctness depends on every successful putBlock updating commit info with the right buffer list and every wait releasing buffers only after the desired replication criteria. `hsync` while a prior async flush is pending must preserve ordering through `lastFlushFuture`.

## Test Signals
`TestBlockOutputStreamCorrectness` and buffer pool tests cover Ratis block output behavior, flushes, commits, buffer release, and ack accounting.
