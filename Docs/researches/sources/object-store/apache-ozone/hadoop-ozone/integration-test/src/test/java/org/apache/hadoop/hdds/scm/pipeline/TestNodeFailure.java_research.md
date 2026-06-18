<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestNodeFailure.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestNodeFailure.java

Purpose: Tests Ratis node-failure detection causing pipeline closure and bounded close-action logging.

Important APIs and types: Uses `MiniOzoneCluster`, `PipelineManager`, `Pipeline`, `PipelineID`, `XceiverServerRatis`, `DatanodeRatisServerConfig`, `RatisReplicationConfig`, `GenericTestUtils.LogCapturer`, and Ratis follower slowness/no-leader timeouts.

Control flow: `BeforeAll` starts six datanodes with datanode pipeline limit one, two-second pipeline reports, and Ratis slowness timeout ten seconds. The test captures `XceiverServerRatis` logs, waits for each Ratis pipeline to be open, shuts down the first node in each pipeline, waits for SCM to mark the pipeline closed or deleted, then counts close-action log tokens.

State and persistence behavior: Pipeline state transitions from open to closed/deleted in SCM due to datanode failure. Datanode runtime Ratis state emits close actions; no persistence is inspected.

Dependencies and integration points: Integrates datanode shutdown, Ratis failure detection, pipeline report handling, SCM pipeline state, and log-based flood protection.

Risks: Log-count assertion is brittle and tied to exact log text `pipeline Action CLOSE`. The wait interval uses `timeForFailure / 2` even though `timeForFailure` is derived from a `Duration` cast path, so timeout unit behavior must remain as expected. Shutdown of first nodes across multiple pipelines can overlap effects.

Test signals: Signals include each pipeline reaching `OPEN`, closure or deletion after first-node shutdown, and exactly two close-action log occurrences.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestNodeFailure.java -->
