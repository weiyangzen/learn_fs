# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/states/Node2PipelineMap.java

## Purpose
`Node2PipelineMap` maintains the in-memory reverse index from datanode ID to pipeline IDs containing that datanode.

## Important APIs, Types, And Functions
`getPipelines` returns a defensive `HashSet` snapshot or an empty set. `getPipelinesCount` returns its size. `addPipeline` adds the pipeline ID to every node in a pipeline. `removePipeline` removes it from each node's set.

## Control Flow
The map is updated when pipeline allocation or removal happens. It uses `ConcurrentHashMap` and concurrent key sets, so add/remove can run without a global lock. Removing a pipeline leaves an empty set in the map rather than removing the datanode key.

## State And Persistence Behavior
State is memory-only. The source comment notes it should be regenerated from pipeline reports on SCM restart. In current integration, `PipelineStateManagerImpl.initialize` repopulates node pipeline membership from the persisted pipeline store.

## Dependencies And Integration Points
The map depends on `DatanodeID`, `DatanodeDetails`, `Pipeline`, and `PipelineID`. It is used by node state management and queried by handlers such as stale/admin node pipeline closers and placement policy pipeline-count logic.

## Risks And Edge Cases
Empty sets remain after removal, which is not functionally wrong but can retain keys. If pipeline membership changes without corresponding add/remove calls, the reverse index becomes stale and can cause missed close operations or incorrect placement limits. Returned sets are snapshots, so concurrent updates are not reflected.

## Test Signals
Tests should cover add/remove for multi-node pipelines, defensive copy behavior, no-pipeline empty result, count after removal, and restart reconstruction from persisted pipelines.
