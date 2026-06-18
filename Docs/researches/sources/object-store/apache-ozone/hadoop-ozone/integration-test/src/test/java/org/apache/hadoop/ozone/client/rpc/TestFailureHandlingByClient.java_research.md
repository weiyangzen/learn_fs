<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestFailureHandlingByClient.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestFailureHandlingByClient.java

Purpose: This integration test exercises Ozone RPC client write recovery when RATIS pipelines, containers, or datanodes fail while a key stream is open. It runs a 10-datanode `MiniOzoneCluster`, writes through `OzoneOutputStream`/`KeyOutputStream`, kills pipeline members or closes containers, and verifies that the client retries to new blocks while OM key length, data content, and exclude-list state remain correct.

Important APIs/types/functions: The fixture configures `RatisClientConfig`, `DatanodeRatisServerConfig`, `OzoneClientConfig`, SCM pipeline limits, and network-topology-aware reads. Tests use `TestHelper.createKey`, `TestHelper.validateData`, `ContainerTestHelper.getFixedLengthString`, `KeyOutputStream.getLocationInfoList`, `getStreamEntries`, `getExcludeList`, SCM `ContainerManager`/`PipelineManager`, and OM `lookupKey`. `testBlockCountOnFailures` opens datanode container RocksDB via `BlockUtils.getDB` and validates `BlockData` chunk count and size.

Control flow: `init` creates volume/bucket and disables stream-buffer flush delay. `restartDownDataNodes` restarts nodes queued by prior tests. `testBlockWritesWithDnFailures` writes 2.5 chunks, kills two replicas, closes the stream, then checks OM data size and physical block accounting. `testWriteSmallFile` forces replacement of a failed first block. `testContainerExclusionWithClosedContainerException` closes a container and expects only the container ID in the exclude list. `testDatanodeExclusionWithMajorityCommit` varies RATIS watch type and verifies datanode exclusion only for `ALL_COMMITTED`. `testPipelineExclusionWithPipelineFailure` kills two nodes and expects pipeline exclusion.

State and persistence behavior: The tests inspect OM key metadata, container metadata tables, block IDs, chunk lists, used block sizes, and client exclude-list contents. They confirm failed chunks do not corrupt committed length and that rewritten data lands in replacement blocks or pipelines.

Dependencies and integration points: Covers Ozone client streaming, SCM pipeline/container lookup, RATIS write/watch semantics, datanode lifecycle operations, container RocksDB block tables, and OM key finalization. It also depends on retry timing and leader election settings to make failures surface quickly.

Risks: The tests are timing-sensitive and one path is marked flaky. They rely on exact failure classification: closed containers, stopped datanodes, and broken pipelines must map to distinct exclude-list dimensions. Assertions that inspect datanode-local DB state can fail if commit-watcher timing changes valid chunk-count scenarios.

Test signals: Successful run proves key data remains readable after mid-stream failures, OM `dataSize` matches user bytes, failed blocks are discarded or rewritten, and exclude lists contain the expected container, datanode, or pipeline identifiers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestFailureHandlingByClient.java -->
