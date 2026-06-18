<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/SimplePipelineProvider.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/SimplePipelineProvider.java

Purpose: `SimplePipelineProvider` creates standalone pipelines. Unlike Ratis, standalone pipelines are immediately OPEN and do not require datanode create or close commands.

Important APIs and types: It extends `PipelineProvider<StandaloneReplicationConfig>` and implements `create` overloads, `createForRead`, and an empty `close`. It uses `pickNodesNotUsed`, `InsufficientDatanodesException`, `PipelineID.randomId`, and `PipelineState.OPEN`.

Control flow: The main `create` gets available unused nodes, verifies there are enough for the requested replication factor, shuffles them, and builds an OPEN pipeline with the first required nodes. The read path creates a pipeline from the datanodes present in replicas.

State and persistence behavior: No state is persisted by this provider. It returns pipeline objects to the pipeline manager, which owns indexing and persistence.

Dependencies and integration points: It integrates with `NodeManager` through the base provider's node picking and is routed through `PipelineFactory` and writable-container allocation for standalone replication.

Risks: The `excludedNodes` and `favoredNodes` parameters are ignored in the main create path. `close` is intentionally a no-op, so callers must not expect datanode cleanup commands for standalone pipelines.

Test signals: Tests should cover insufficient datanode exceptions, node count and state on created pipelines, random selection not exceeding requested factor, read pipeline construction from replicas, and no-op close behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/SimplePipelineProvider.java -->
