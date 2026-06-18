# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineActionHandler.java

## Purpose
`PipelineActionHandler` handles datanode-sent pipeline actions, currently closing pipelines when datanodes request a close.

## Important APIs, Types, And Functions
It implements `EventHandler<PipelineActionsFromDatanode>`. `onMessage` iterates pipeline actions and delegates to `processPipelineAction`. That method extracts action, pipeline ID, and detailed reason; verifies current SCM leadership; calls `pipelineManager.closePipeline` for `CLOSE`; and handles unknown pipelines with `closeUnknownPipeline`, which sends `ClosePipelineCommand` back to the reporting datanode.

## Control Flow
Non-leader SCMs log and ignore actions. Leaders process only `PipelineAction.Action.CLOSE`; unknown action types are logged as errors. If the pipeline is not found, SCM assumes the datanode has stale state and sends a close command with the current leader term through the event bus. `SCM_NOT_LEADER` errors are treated as leadership races and logged less severely.

## State And Persistence Behavior
The handler owns no state. Persistent pipeline transitions are delegated to `PipelineManager.closePipeline`; command queue persistence/delivery is delegated through `SCMEvents.DATANODE_COMMAND`.

## Dependencies And Integration Points
It depends on datanode heartbeat-dispatched `PipelineActionsFromDatanode`, protobuf `PipelineAction`, `PipelineManager`, `SCMContext`, SCM event bus, and Ozone close-pipeline commands.

## Risks And Edge Cases
Leadership can change between `isLeader` and `getTermOfLeader`, so `NotLeaderException` is handled. Unknown pipeline close commands prevent datanodes from keeping orphan pipelines, but failures to send due to leadership race leave cleanup to future reports. Only CLOSE is supported; adding new actions requires explicit handling.

## Test Signals
Tests should cover leader vs follower behavior, close action success, unknown action logging, missing-pipeline close-command emission with term, and `SCM_NOT_LEADER` handling.
