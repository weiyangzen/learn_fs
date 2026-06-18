# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/ECPipelineProvider.java

## Purpose
`ECPipelineProvider` creates EC pipelines and read pipelines for EC containers. It assigns EC replica indexes to selected datanodes and sorts read pipelines by node health.

## Important APIs, Types, And Functions
It extends `PipelineProvider<ECReplicationConfig>`. `create(replicationConfig)` delegates with empty excluded/favored lists. The placement-aware `create` asks an EC placement policy for `replicationConfig.getRequiredNodes()` datanodes with configured container size. The node-list `create` assigns replica indexes starting at 1. `createForRead` builds a datanode-to-replica-index map from replicas, skips dead or unknown nodes, sorts by `CREATE_FOR_READ_COMPARATOR`, and creates an allocated pipeline. `close` is a no-op.

## Control Flow
Write pipeline creation is placement-policy driven. Read pipeline creation iterates current replicas, consults `NodeManager.getNodeStatus`, filters out dead nodes and missing nodes, records indexes from `ContainerReplica`, sorts healthier nodes first and dead last by comparator, then builds a pipeline with the original replica-index map.

## State And Persistence Behavior
The provider is stateless aside from references to configuration, node manager, state manager, placement policy, and container size. It creates `Pipeline` objects in `ALLOCATED` state; persistence occurs only when the pipeline manager adds them.

## Dependencies And Integration Points
It depends on `ECReplicationConfig`, `PlacementPolicy`, `NodeManager`, `NodeStatus`, `ContainerReplica`, and `PipelineStateManager`. `PipelineFactory` owns the EC provider.

## Risks And Edge Cases
`createForRead` can return fewer nodes than the EC config requires if replicas are missing, unknown, or dead; that may be valid for degraded reads but needs callers to understand it. Sorting uses node status map lookups and assumes all DNS in the list have entries. `close` is empty because EC datanodes do not need the same close command semantics as Ratis pipelines, so lifecycle changes rely on SCM state and container handling.

## Test Signals
Tests should verify EC write placement size and index assignment, excluded/favored node propagation, read-pipeline filtering for dead/unknown nodes, comparator ordering for healthy/stale/operational states, and behavior with partial EC replica sets.
