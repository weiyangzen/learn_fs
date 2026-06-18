# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineProvider.java

## Purpose
`PipelineProvider` is the abstract base for replication-type-specific pipeline creation and close logic.

## Important APIs, Types, And Functions
Subclasses implement placement-aware `create`, explicit-node `create`, read `createForRead`, and `close`. The base stores `NodeManager` and `PipelineStateManager`. Helper methods `pickNodesNotUsed` and `pickAllNodesNotUsed` select in-service healthy nodes not already used by open, dormant, or allocated pipelines with the same replication config, optionally enforcing metadata/data space requirements.

## Control Flow
`pickAllNodesNotUsed` collects all datanodes used by active pipelines for the requested replication config, then filters healthy nodes to those not in that set. It throws `SCMException` if fewer candidates exist than required. `pickNodesNotUsed` limits to required count; the size-aware variant additionally filters with `SCMCommonPlacementPolicy.hasEnoughSpace` before limiting and throws a space-specific `SCMException` if insufficient.

## State And Persistence Behavior
The provider base is stateless aside from manager references. It reads pipeline state and node state but does not mutate or persist them.

## Dependencies And Integration Points
It depends on `ReplicationConfig`, `PipelineStateManager`, `NodeManager`, `NodeStatus`, `ContainerReplica`, `SCMCommonPlacementPolicy`, and `SCMException`. `SimplePipelineProvider`, `RatisPipelineProvider`, and `ECPipelineProvider` extend it.

## Risks And Edge Cases
The no-arg constructor sets managers to null for tests/subclasses; helper methods will fail if used on such instances. Parallel stream filtering depends on correct `DatanodeDetails.equals`. Selection order is not strongly defined after parallel collection, which can affect deterministic tests. Active-state filtering excludes only OPEN, DORMANT, and ALLOCATED pipelines.

## Test Signals
Tests should cover node exclusion by active pipelines, closed pipelines not excluding nodes, insufficient healthy nodes, insufficient space, required-node limiting, and behavior of subclasses using explicit vs helper-based placement.
