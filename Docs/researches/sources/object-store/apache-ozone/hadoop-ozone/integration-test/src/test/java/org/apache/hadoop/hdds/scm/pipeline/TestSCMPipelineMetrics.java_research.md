<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestSCMPipelineMetrics.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestSCMPipelineMetrics.java

Purpose: Verifies `SCMPipelineMetrics` counters for pipeline creation, destruction, and per-pipeline block allocation metric lifecycle.

Important APIs and types: Uses `NonHATests.TestCase`, `SCMPipelineMetrics`, `PipelineManager`, `Pipeline`, `AllocatedBlock`, SCM block manager `allocateBlock`, `ExcludeList`, `RatisReplicationConfig`, and metrics assertion helpers.

Control flow: Setup captures the shared MiniOzoneCluster. Tests read the pipeline-created counter after cluster startup, close/delete the first available pipeline and assert the destroyed counter increments, allocate a block on a Ratis one pipeline, read the generated per-pipeline block allocation metric, then close the pipeline via client protocol and assert that metric is no longer exported.

State and persistence behavior: Pipeline manager state changes when a pipeline is deleted or closed. Metrics state is registered and unregistered with pipeline lifecycle. Block allocation updates per-pipeline counters.

Dependencies and integration points: Covers SCM pipeline metrics source, SCM block manager, client protocol close pipeline path, and dynamic metric-name generation based on pipeline identity.

Risks: Uses the first pipeline from a shared test cluster, so concurrent tests or fixture changes can affect available pipeline type/state. The final assertion expects an `AssertionError` from missing metric lookup rather than a zero value.

Test signals: Signals include positive `NumPipelineCreated`, `NumPipelineDestroyed` increment by one, positive per-pipeline block allocation counter, and absence of that metric after pipeline closure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestSCMPipelineMetrics.java -->
