<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestLeaderChoosePolicy.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestLeaderChoosePolicy.java

Purpose: Tests Ratis pipeline leader-selection policies, including balanced suggested leaders and persistence of suggested leader IDs across SCM restart.

Important APIs and types: Uses `MiniOzoneCluster`, `PipelineManager`, `Pipeline`, `DatanodeID`, `RatisReplicationConfig`, `MinLeaderCountChoosePolicy`, `DefaultLeaderChoosePolicy`, and configuration keys for datanode pipeline limits, Ratis pipeline limits, factor-one auto creation, and leader choosing policy.

Control flow: `init` starts a cluster with tuned heartbeat intervals and configured pipeline limits. `checkLeaderBalance` waits for each pipeline's actual leader to match its suggested leader, counts leaders per datanode, and asserts balance. Tests disable factor-one creation, select policy implementation by class name, wait for three Ratis three pipelines, close random pipelines in a loop, and restart SCM to compare persisted suggested leaders.

State and persistence behavior: Pipeline state and suggested leader IDs are persisted in SCM metadata and reloaded after restart. Runtime leader state is reported by Ratis and compared against SCM's suggested leader.

Dependencies and integration points: Integrates pipeline auto-creation, leader selection implementations, SCM restart recovery, Ratis leader reports, and pipeline manager state.

Risks: The class is annotated `@Unhealthy("This test was never enabled")`, indicating known instability or disabled status. Random pipeline destruction can close multiple pipelines per iteration. Balance assertions assume exact equal distribution and actual leader convergence to suggested leader.

Test signals: Signals include expected Ratis three pipeline counts, no factor-one pipelines when disabled, each datanode having one leader under min-leader policy, persisted pipeline count after restart, matching pipeline IDs and suggested leaders before and after restart, and default policy creating pipelines without balance assertions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestLeaderChoosePolicy.java -->
