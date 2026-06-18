<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestOzoneClientRetriesOnExceptionFlushDelay.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestOzoneClientRetriesOnExceptionFlushDelay.java

Purpose: This flush-delay variant checks that a `GroupMismatchException` during a buffered block write is detected, translated through `HddsClientUtils.checkForException`, and recovered by allocating a replacement block.

Important APIs/types/functions: The fixture configures `OzoneClientConfig` checksum type and retry count, small `ClientConfigForTesting` buffer sizes, SCM close/scrub/destroy timing, `XceiverClientManager`, and `MiniOzoneCluster`. The test uses `ContainerTestHelper.getCreateContainerRequest` to deliberately create a duplicate container in the target RATIS group and provoke a group mismatch.

Control flow: `testGroupMismatchExceptionHandling` initiates a one-block key, resolves the first block's container and pipeline, sends a create-container command through an acquired xceiver client, writes data larger than the max flush size, extracts the first `BlockOutputStream`, waits for pipeline close, and flushes. It then asserts the underlying stream exception is `GroupMismatchException`, the failed pipeline ID is in the `KeyOutputStream` exclude list, a second stream entry has been allocated, close clears stream entries, and the key validates with the original bytes.

State and persistence behavior: Client state under test includes stream entries, pipeline exclude-list contents, and the stored `ioException`. Persistent validation is final OM key/readback state.

Dependencies and integration points: Covers delayed flush buffering, block-output retry, xceiver client commands, RATIS pipeline close detection, and OM finalization after retry.

Risks: Artificially sending create-container commands relies on low-level container protocol behavior. Timing around pipeline close and flush can be sensitive.

Test signals: Passing proves group mismatch in the flush-delay path does not lose data and correctly excludes the failing pipeline before retry.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestOzoneClientRetriesOnExceptionFlushDelay.java -->
