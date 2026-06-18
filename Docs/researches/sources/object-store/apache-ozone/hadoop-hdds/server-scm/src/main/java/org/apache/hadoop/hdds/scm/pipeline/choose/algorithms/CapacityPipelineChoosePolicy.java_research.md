<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/choose/algorithms/CapacityPipelineChoosePolicy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/choose/algorithms/CapacityPipelineChoosePolicy.java

Purpose: `CapacityPipelineChoosePolicy` biases writable-container allocation toward less utilized pipelines using the "power of two choices" strategy: choose two healthy random candidates and pick the one with lower node utilization.

Important APIs and types: It implements `PipelineChoosePolicy` with `init`, `choosePipeline`, and `choosePipelineIndex`. It uses `NodeManager.getNodeStat`, `SCMNodeMetric`, and an inner `CapacityPipelineComparator`.

Control flow: `choosePipeline` asks `HealthyPipelineChoosePolicy` for two candidate pipelines, compares their sorted datanode utilization metrics, and returns the lower-utilization pipeline. Metrics for each pipeline are gathered from nodes, sorted, pushed into a stack-like deque, and compared node by node.

State and persistence behavior: The only state is the initialized `NodeManager` and the composed health policy. It does not persist decisions.

Dependencies and integration points: The policy plugs into SCM's pipeline choose factory and is used by writable container selection. Its behavior depends on node usage metrics being current.

Risks: If the input list is empty, the nested random policy can fail. Null node metrics are filtered out, so incomplete node stats can make comparisons shorter or tie unexpectedly. `choosePipelineIndex` copies the input list and then uses `indexOf`, relying on pipeline equality.

Test signals: Tests should cover lower-utilization selection, same-pipeline comparison, null metrics, unhealthy candidate fallback through the health policy, empty input behavior, and index mapping back to the original list.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/choose/algorithms/CapacityPipelineChoosePolicy.java -->
