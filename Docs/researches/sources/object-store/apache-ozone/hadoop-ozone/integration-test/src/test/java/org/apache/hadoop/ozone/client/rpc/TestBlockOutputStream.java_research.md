# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestBlockOutputStream.java

## Purpose
`TestBlockOutputStream` is the baseline integration test for RATIS `RatisBlockOutputStream` buffering, flushing, commit watching, metrics, and data durability. It uses a `MiniOzoneCluster` with five datanodes, tiny client-side buffer sizes, checksum disabled, HBase enhancement flags enabled, and RATIS/client timeouts tuned low enough to exercise synchronous and asynchronous flush paths without long hangs.

## Important APIs, types, and functions
The class exposes reusable package-private helpers used by later failure tests: `createCluster()`, `createCluster(int)`, `newClientConfig(...)`, `newClient(...)`, `createKey(...)`, and `getKeyName()`. The constants `CHUNK_SIZE`, `FLUSH_SIZE`, `MAX_FLUSH_SIZE`, `BLOCK_SIZE`, `VOLUME`, and `BUCKET` define the miniature block geometry. Tests inspect `OzoneOutputStream`, `KeyOutputStream`, `RatisBlockOutputStream`, `BufferPool`, and `XceiverClientMetrics`; metrics are checked for `WriteChunk`, `PutBlock`, pending operation counts, and total operation counts.

## Control flow
`createCluster` builds the cluster, waits for a factor-three pipeline, and creates a volume/bucket. Each parameterized test runs for all combinations of `streamBufferFlushDelay` and put-block piggybacking. The test body writes a specific byte count, unwraps the stream stack, checks buffer count and stream-entry count, optionally calls `flush()`, closes the key, checks post-close cleanup, and finally reads back the key through `TestHelper.validateData`.

The tested write-size regimes are: less than a chunk, exactly flush size, more than one chunk but below flush size, more than flush size, exactly max flush size, and more than max flush size. These regimes intentionally trigger different transitions: data sitting only in memory, flush-size automatic write chunking, explicit flush, full-buffer `watchForCommit`, and close-time final `PutBlock`.

## State and persistence behavior
The test asserts internal stream state directly: `writtenDataLength`, `totalDataFlushedLength`, `totalAckDataLength`, `commitIndex2flushedDataMap`, `BufferPool` size, and `computeBufferData()`. It verifies that close drains stream entries, clears commit-index tracking, and leaves no buffered data. Persistence is validated by rereading keys from the object store, while OM and datanode persistence details are exercised indirectly through actual RATIS writes.

## Dependencies and integration points
This file integrates Ozone client RPC, SCM pipeline allocation, RATIS block streaming, datanode container operations, and metrics. It depends on `ClientConfigForTesting` to force small chunks and flush windows, `OzoneClientFactory.getRpcClient` for client variants, and `TestHelper.createKey`/`validateData` for object-store interactions.

## Risks and test signals
Several tests are annotated `@Flaky("HDDS-11564")`, reflecting timing sensitivity around asynchronous operation completion. Assertions sometimes allow pending counts to be less than or equal to expected values because write and put-block operations can complete before the assertion. The strongest signals are metric deltas, stream cleanup after close, exact ack/flushed lengths, and successful readback for every flush-delay/piggybacking combination.
