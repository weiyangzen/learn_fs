<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestRatisPipelineCreateAndDestroy.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestRatisPipelineCreateAndDestroy.java

Purpose: Tests automatic Ratis pipeline creation after pipeline destruction, optional factor-one auto creation, and pipeline creation behavior when datanodes are stopped and restarted.

Important APIs and types: Uses `MiniOzoneCluster`, `PipelineManager`, `Pipeline`, `HddsDatanodeService`, `RatisReplicationConfig`, `NodeStatus.inServiceHealthy`, `SCMException.ResultCodes.FAILED_TO_FIND_SUITABLE_NODE`, and `SCMService.Event.PRE_CHECK_COMPLETED`.

Control flow: `init` starts a cluster with datanode pipeline limit two and fast pipeline creation interval. The first test waits for two Ratis three pipelines and six factor-one pipelines, closes all open Ratis three pipelines, and waits for replacements. The second disables factor-one auto creation and repeats replacement checks. The restart test starts three datanodes, shuts all down, waits for zero healthy in-service nodes, asserts explicit Ratis three creation fails, waits for open pipeline count to drop, restarts datanodes, closes old pipelines, triggers pre-check completion, and waits for a new pipeline.

State and persistence behavior: Pipeline manager runtime state is mutated through close operations and node liveness changes. The test does not restart SCM, but it checks automatic background services react to pipeline deletion and node availability.

Dependencies and integration points: Covers pipeline creator service, node manager health accounting, factor-one pipeline policy, SCM service manager pre-check events, and placement failure reporting.

Risks: `waitForPipelines(0)` uses `size() >= numPipelines`, so passing zero returns immediately and does not actually wait for destruction. Replacement timing depends on background pipeline creation. Datanode restart branch only waits if enough nodes report healthy.

Test signals: Signals include at least two open Ratis three pipelines after startup and after destruction, factor-one pipeline count equal to datanode count or zero depending on config, explicit creation failure with `FAILED_TO_FIND_SUITABLE_NODE`, zero in-service healthy nodes after shutdown, and new pipeline creation after datanode restart plus pre-check event.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestRatisPipelineCreateAndDestroy.java -->
