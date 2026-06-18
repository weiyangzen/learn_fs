<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/safemode/TestSCMSafeModeWithPipelineRules.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/safemode/TestSCMSafeModeWithPipelineRules.java

Purpose: Tests SCM safe-mode exit behavior governed by healthy-pipeline and one-replica-pipeline safe-mode rules after SCM restart with only partial datanode recovery.

Important APIs and types: Uses `MiniOzoneCluster`, `PipelineManager`, `SCMSafeModeManager`, `HealthyPipelineSafeModeRule`, `OneReplicaPipelineSafeModeRule`, `SafeModeRuleFactory`, `ReplicationManager`, `RatisReplicationConfig`, and `SCMContainerPlacementCapacity`.

Control flow: Setup starts six datanodes with one Ratis three pipeline per three nodes, factor-one pipelines, same-peer disallowance, and long post-safe-mode pipeline creation interval. The test waits for initial pipelines, stops the cluster, restarts OM and SCM without datanodes, restarts all datanodes from one Ratis three pipeline, validates the healthy-pipeline rule but not the one-replica rule, then restarts one datanode from the second pipeline and waits for full safe-mode exit.

State and persistence behavior: Pipeline metadata is persisted and reloaded by SCM even when datanodes are not all alive. Safe-mode rule state is computed from datanode reports and persisted pipeline membership. Replication manager should start only after safe-mode prechecks finish.

Dependencies and integration points: Covers SCM safe-mode rule factory, pipeline reports, persisted pipeline metadata, datanode restart, OM/SCM restart ordering, and replication-manager activation after safe mode.

Risks: The test depends on exact thresholds: `ceil(0.1 * 2)` and `ceil(0.9 * 2)` for two Ratis three pipelines. Directly using `pipelineList.get(1)` assumes two pipelines exist and stable ordering. Long waits are needed because partial datanode restart controls rule validation.

Test signals: Signals include initial Ratis one and three pipeline counts, healthy-pipeline rule validating after one full pipeline reports, one-replica rule remaining false until a second pipeline member reports, SCM remaining in safe mode before that, SCM exiting safe mode afterward, original total pipeline count retained during wait duration, and replication manager running.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/safemode/TestSCMSafeModeWithPipelineRules.java -->
