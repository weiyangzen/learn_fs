# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/StartDatanodeAdminHandler.java

## Purpose
`StartDatanodeAdminHandler` reacts when a datanode begins an admin workflow, such as decommission or maintenance, by closing all pipelines that include that datanode.

## Important APIs, Types, And Functions
It implements `EventHandler<DatanodeDetails>`. `onMessage` asks `NodeManager` for the datanode's pipelines and calls `PipelineManager.closePipeline` for each.

## Control Flow
The flow mirrors `StaleNodeHandler`: log the admin-start event, iterate the pipeline IDs, attempt close, and log any `IOException` without failing the event handler loop.

## State And Persistence Behavior
The handler has no internal mutable state. It delegates state changes to the pipeline manager, which persists pipeline state transitions through SCM HA/Ratis and the pipeline store in the implementation.

## Dependencies And Integration Points
It integrates with SCM's admin/decommission/maintenance event path. It depends on node-to-pipeline membership being current enough to close write paths before admin operations proceed.

## Risks And Edge Cases
Snapshot pipeline membership can miss concurrent additions. Failure to close a pipeline only logs, so callers need separate admin workflow checks to ensure pipeline drain actually completed. The handler closes all pipelines regardless of whether they are already closing or closed; idempotence depends on `PipelineManager`.

## Test Signals
Tests should cover decommission/maintenance start events, multiple pipeline closure, empty memberships, and IOException handling.
