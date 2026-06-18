<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestOzoneClientRetriesOnExceptions.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestOzoneClientRetriesOnExceptions.java

Purpose: This class tests the non-flush-delay retry path in `BlockOutputStream` and `KeyOutputStream`, including recovery from group mismatch and failure after exceeding the configured client retry count.

Important APIs/types/functions: Setup sets `OzoneClientConfig.maxRetryCount`, disables checksums and stream flush delay, applies small block/chunk/flush sizes, and uses `RoundRobinPipelineChoosePolicy` to diversify allocated containers. It uses `XceiverClientManager`, `XceiverClientSpi`, `ContainerTestHelper.getCreateContainerRequest`, `BlockOutputStream.getIoException`, `HddsClientUtils.checkForException`, `GroupMismatchException`, and `ContainerNotOpenException`.

Control flow: `testGroupMismatchExceptionHandling` creates one key, provokes duplicate container creation on the selected pipeline, writes and flushes after pipeline close, verifies a `GroupMismatchException`, checks pipeline exclusion, confirms a second stream entry was allocated, closes, and validates data. `testMaxRetriesByOzoneClient` preallocates `MAX_RETRIES + 1` blocks, deliberately closes each candidate container, writes data, waits for close, and then expects a write/flush failure once retries exceed the configured max. A subsequent `flush` must report that the stream is closed.

State and persistence behavior: The tests inspect client stream entries before and after close, the exclude list, per-block stream exceptions, and final key readback for the recoverable case. The max-retry case validates fail-fast client state after exhausting replacement blocks.

Dependencies and integration points: Integrates SCM placement policy, low-level xceiver container commands, client retry counters, exception unwrapping, and OM/object-store validation.

Risks: Assumptions require enough distinct containers to exceed retry count; if placement reuses containers, the test can be skipped by `Assumptions.assumeTrue`. Exception class mapping is a brittle but important API contract.

Test signals: Passing means recoverable container/protocol failures retry to a new block, and unrecoverable repeated failures produce a clear max-retry IOException and close the stream.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestOzoneClientRetriesOnExceptions.java -->
