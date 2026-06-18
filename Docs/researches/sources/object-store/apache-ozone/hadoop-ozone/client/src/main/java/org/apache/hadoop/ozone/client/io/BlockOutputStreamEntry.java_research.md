## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/BlockOutputStreamEntry.java

### Purpose
`BlockOutputStreamEntry` wraps an output stream for writing one allocated block through DataNode pipelines. The base implementation creates a `RatisBlockOutputStream`, tracks attempted write position, handles flush/hsync/close, and supports retry handoff coordination.

### Important APIs and Types
State includes config, lazy `BlockOutputStream`, block ID, key, xceiver client factory, pipeline, intended length, current position, block token, buffer pool, metrics, stream buffer args, executor supplier, retry-handling flag, and inflight call count. APIs include `write`, `flush`, `hsync`, `close`, `cleanup`, `writeOnRetry`, ack/written length queries, failed-server query, position management, retry wait/finish methods, and a builder.

### Control Flow
`checkStream` lazily calls `createOutputStream`, which constructs `RatisBlockOutputStream`. Writes delegate to the underlying stream and increment current position. `hsync` requires the underlying stream to implement `Syncable` and records latency via metrics. `close` closes the stream and refreshes block ID to capture updated BCSID. Retry coordination uses `isHandlingRetry`, a `Condition`, and inflight call counters so a replacement entry can finish replay before normal writes resume.

### State and Persistence Behavior
The entry stores local write position and block ID while the underlying stream persists data to DataNodes. `resetToAckedPosition` rolls local position back to acknowledged bytes after failure. Cleanup delegates to the underlying block stream and may invalidate the xceiver client.

### Dependencies and Integration Points
It integrates with HDDS `BlockOutputStream`, `RatisBlockOutputStream`, `BufferPool`, `ContainerClientMetrics`, `StreamBufferArgs`, `XceiverClientFactory`, `Pipeline`, block tokens, Java executor services, Hadoop `Syncable`, and higher-level key output streams.

### Risks and Edge Cases
Current position records successful write-call bytes, not necessarily fully acknowledged bytes; retry paths must use ack length correctly. `waitForRetryHandling` depends on callers holding the associated lock for the condition. `cleanup` initializes the stream if needed, similar to the data-stream entry. Hsync on a non-`Syncable` implementation throws `UnsupportedOperationException`.

### Test Signals
Tests should verify lazy stream creation, position increments, block ID refresh on close/ack, `resetToAckedPosition`, retry wait/signal behavior, inflight call accounting, hsync metrics and unsupported stream handling, failed-server propagation, cleanup invalidation, and builder propagation of retry mode and stream dependencies.
