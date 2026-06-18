# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/StaleNodeHandler.java

## Purpose
`StaleNodeHandler` reacts to a datanode entering stale health state by closing/finalizing all pipelines that include that datanode.

## Important APIs, Types, And Functions
It implements `EventHandler<DatanodeDetails>`. The constructor receives `NodeManager` and `PipelineManager`. `onMessage` fetches pipeline IDs from `nodeManager.getPipelines(datanodeDetails)` and calls `pipelineManager.closePipeline` for each.

## Control Flow
On an event, it logs the stale transition and the affected pipeline set. It iterates the set and attempts to close each pipeline independently. `IOException` from any close is logged and does not stop processing of other pipelines.

## State And Persistence Behavior
The handler owns no state beyond collaborator references. Persistent effects are delegated to `PipelineManager.closePipeline`, which may update pipeline/container state and emit close-container events through its implementation.

## Dependencies And Integration Points
It is wired into SCM's event queue for stale-node events. It depends on `NodeManager` membership tracking and `PipelineManager` lifecycle transitions.

## Risks And Edge Cases
The pipeline set is a snapshot; pipelines added or removed concurrently may not be represented. Exceptions are logged at info level without retry. Closing a pipeline can have broad side effects, including container finalization, so stale detection thresholds affect write availability.

## Test Signals
Tests should verify all pipelines for a stale node are closed, failures on one pipeline do not skip subsequent pipelines, and empty pipeline sets are harmless.
