<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestMultiBlockWritesWithDnFailures.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestMultiBlockWritesWithDnFailures.java

Purpose: This class tests multi-block RATIS writes when datanodes fail after some blocks have already been allocated or preallocated. It ensures stream close reconciles successful and retried blocks into correct OM length and readable data.

Important APIs/types/functions: The fixture configures RATIS client/server timeouts, SCM stale-node interval, leader election timeout, pipeline limit, and a `MiniOzoneCluster`. Tests use `OzoneOutputStream`, `KeyOutputStream.getLocationInfoList`, `getStreamEntries`, `BlockOutputStreamEntry`, SCM container/pipeline lookup, `shutdownHddsDatanode`, OM `lookupKey`, and `TestHelper.validateData`.

Control flow: `testMultiBlockWritesWithDnFailures` writes data spanning more than one block, confirms two block locations, shuts down two nodes from the second block's pipeline, writes the same data again, closes, then checks OM size equals two writes. `testMultiBlockWritesWithIntermittentDnFailures` preallocates six blocks, writes two data spans, kills one pipeline node, writes again, kills a second node, writes a fourth span, closes, and validates final length/content.

State and persistence behavior: The tests observe client block-location state and OM key metadata after close. They do not inspect container-local RocksDB, but they depend on OM discarding failed preallocated locations and counting only successfully committed user bytes.

Dependencies and integration points: Covers KeyOutputStream retry and block-preallocation behavior, SCM pipeline lookup, datanode shutdown, RATIS failure handling, and OM key finalization.

Risks: The intermittent-failure case is marked flaky and is sensitive to exactly when failed pipelines are detected. Preallocation count and pipeline placement can change with SCM policy settings.

Test signals: Passing indicates multi-block client writes recover from one or two datanode failures, close without losing data, and persist the expected key size in OM.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestMultiBlockWritesWithDnFailures.java -->
