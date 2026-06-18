<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineStateMap.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineStateMap.java

Purpose: `PipelineStateMap` is the non-thread-safe in-memory index behind SCM pipeline state. It stores `PipelineID -> Pipeline`, `PipelineID -> sorted ContainerID set`, and an optimized `ReplicationConfig -> open pipeline list` cache used by common allocation queries.

Important APIs and types: Core methods are `addPipeline`, `addContainerToPipeline`, `addContainerToPipelineSCMStart`, `getPipeline`, `getPipelines` overloads, `getPipelineCount`, `getContainers`, `removePipeline`, `removeContainerFromPipeline`, and `updatePipelineState`. It depends on `Pipeline`, `PipelineID`, `PipelineState`, `ReplicationConfig`, `ContainerID`, `DatanodeDetails`, and the pipeline exceptions.

Control flow: Adding a pipeline validates node count against required replication nodes, rejects duplicate IDs, creates an empty container set, and indexes open pipelines by replication config. Query methods either read the open-pipeline cache or scan all pipelines and then filter by replication config, state, excluded datanodes, and excluded pipeline IDs. State updates replace the immutable pipeline object via builder and maintain the open-pipeline cache.

State and persistence behavior: This class persists nothing itself; durability is supplied by higher-level managers. Its invariant is that every pipeline has both a `pipelineMap` entry and a `pipeline2container` entry. The SCM-start container-add path deliberately tolerates open containers attached to already closed pipelines because SCM DB flush ordering can leave that state after restart.

Dependencies and integration points: `PipelineStateManagerImpl` owns synchronization and persistence around this map. Container allocation, close pipeline handling, safe mode rules, and pipeline reports rely on its state-specific queries and container membership. The open-pipeline cache is a performance-sensitive integration point.

Risks: Callers must hold appropriate locks because the map and cached lists are thread-unsafe. Removing a pipeline requires closed state but does not check whether containers remain. Any equality/hash behavior change on `Pipeline` could affect removal from `query2OpenPipelines`.

Test signals: Useful tests assert duplicate detection, state-cache updates across ALLOCATED/OPEN/CLOSED transitions, exclude filtering, SCM restart container attachment, closed-pipeline removal rejection, and returned collection copy isolation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineStateMap.java -->
