# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineStateManager.java

## Purpose
`PipelineStateManager` defines the replicated state-management contract for SCM pipelines and their container memberships.

## Important APIs, Types, And Functions
Replicated methods marked with `@Replicate` include `addPipeline`, `removePipeline`, and `updatePipelineState`, each using protobuf IDs/states suitable for SCM Ratis. Non-replicated methods manage container membership, lookup pipelines by ID/config/state, count pipelines, close, and reinitialize from a DB table. The default `getType` returns SCM Ratis request type `PIPELINE`.

## Control Flow
Implementations are expected to replicate pipeline add/remove/state-update operations through SCM HA before applying them. Container membership changes are local state operations around the pipeline state map and are not annotated in this interface.

## State And Persistence Behavior
The interface does not own state but explicitly models a persistent `Table<PipelineID, Pipeline>` reload path. Implementations must keep in-memory state and durable state consistent.

## Dependencies And Integration Points
It extends `SCMHandler`, uses SCM Ratis protocol request types, DB table abstractions, `ReplicationConfig`, `Pipeline`, `PipelineID`, `ContainerID`, and SCM metadata replication annotations. `PipelineManagerImpl` is the primary caller.

## Risks And Edge Cases
Clear separation between replicated and non-replicated methods is critical. If callers bypass replicated paths for add/remove/state transitions, HA followers can diverge. Reinitialize must also rebuild node reverse indexes, not just pipeline maps.

## Test Signals
Tests should validate replication annotations/proxy behavior, DB reload, pipeline lookup filters, container membership rules, and consistency between pipeline store and node manager after add/remove/reinitialize.
