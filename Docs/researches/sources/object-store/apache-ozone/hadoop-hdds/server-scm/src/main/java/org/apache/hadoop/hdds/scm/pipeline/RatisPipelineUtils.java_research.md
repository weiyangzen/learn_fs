<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/RatisPipelineUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/RatisPipelineUtils.java

Purpose: `RatisPipelineUtils` currently contains one package-private helper that finds other open or non-closed Ratis factor THREE pipelines sharing the same datanode set as a supplied pipeline.

Important APIs and types: `checkPipelineContainSameDatanodes(PipelineStateManager, Pipeline)` queries `RatisReplicationConfig.getInstance(ReplicationFactor.THREE)`, filters out the input pipeline ID, ignores CLOSED pipelines, and uses `Pipeline.sameDatanodes`.

Control flow: The method reads all Ratis THREE pipelines from the state manager, streams through them, applies the ID, state, and datanode-set filters, and returns a collected list.

State and persistence behavior: There is no state or persistence here. The function is a derived query over the pipeline state manager's current view.

Dependencies and integration points: It is used by pipeline management logic that detects duplicate datanode groupings and increments related metrics. It depends on `Pipeline.sameDatanodes` rather than list order.

Risks: It only checks Ratis factor THREE, so future replication configs need separate logic. It treats ALLOCATED and OPEN duplicates as relevant but skips only CLOSED; stale non-closed pipelines can therefore suppress or flag creation.

Test signals: Tests should verify same datanodes in different order are matched, self is excluded, CLOSED matches are skipped, and non-Ratis or non-THREE pipelines are ignored.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/RatisPipelineUtils.java -->
