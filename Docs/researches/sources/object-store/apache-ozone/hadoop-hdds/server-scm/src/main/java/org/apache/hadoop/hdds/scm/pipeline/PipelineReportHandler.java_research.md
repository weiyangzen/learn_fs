# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineReportHandler.java

## Purpose
`PipelineReportHandler` processes pipeline reports sent by datanodes during heartbeats. It records reported datanodes and leaders, opens healthy allocated pipelines, notifies safemode rules, and commands datanodes to close unknown pipelines.

## Important APIs, Types, And Functions
It implements `EventHandler<PipelineReportFromDatanode>`. `onMessage` validates the report wrapper and iterates each protobuf `PipelineReport`. `processPipelineReport` resolves the pipeline, calls `setReportedDatanode`, calls `setPipelineLeaderId`, opens allocated healthy pipelines, and fires `OPEN_PIPELINE` while SCM is in safemode. `handlePipelineNotFoundException` sends `ClosePipelineCommand` to the reporting datanode if SCM is leader. `isNotLeaderException` suppresses noisy follower errors.

## Control Flow
For each reported pipeline, missing pipeline IDs are handled separately from other IO/timeouts. Existing pipelines mark the reporting datanode through `pipeline.reportDatanode`. If the report says the datanode is leader, or the pipeline is Ratis factor one where no leader flag exists, the pipeline leader ID is set to that datanode. Allocated pipelines transition to open only after `pipeline.isHealthy()` becomes true, meaning enough expected reports have arrived. Healthy reports in safemode fire an event for safemode exit rules.

## State And Persistence Behavior
The handler mutates `Pipeline` objects in memory by recording reported nodes and leader ID. Opening a pipeline delegates to `PipelineManager.openPipeline`, which persists state through the state manager. Unknown-pipeline close commands are queued through the event bus.

## Dependencies And Integration Points
It depends on datanode heartbeat dispatcher wrappers, `SafeModeManager`, `PipelineManager`, `SCMContext`, SCM events, protobuf reports, Ratis replication config helpers, and close-pipeline commands.

## Risks And Edge Cases
Follower SCMs may attempt operations that throw `SCM_NOT_LEADER`; the handler suppresses those only for `SCMException`. Unknown pipelines are only commanded closed by leaders. Pipeline object mutation through `reportDatanode` and `setLeaderId` must be thread-safe with concurrent reads. Factor-one leader assignment assumes the reporter is the only/valid leader.

## Test Signals
Tests should cover allocated pipeline opening only after all required reports, leader ID assignment for factor one and leader-flag reports, safemode `OPEN_PIPELINE` event emission, unknown-pipeline close command emission, follower/no-leader behavior, and exception handling for IO/timeouts.
