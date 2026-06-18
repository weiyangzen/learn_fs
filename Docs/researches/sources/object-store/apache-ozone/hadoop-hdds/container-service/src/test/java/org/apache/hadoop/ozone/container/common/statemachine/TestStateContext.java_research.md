# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/TestStateContext.java

## Purpose
`TestStateContext` validates `StateContext`, the datanode state-machine context that stores reports, actions, command queues, leader SCM term, endpoint queues, and task execution state. It checks both heartbeat-facing data queues and datanode-state execution safeguards.

## Important APIs, Types, And Functions
- Report APIs: `refreshFullReport`, `addIncrementalReport`, `putBackReports`, `getAllAvailableReports`, `getAllAvailableReportsUpToLimit`, `getFullContainerReportDiscardPendingICR`, `getContainerReports`, `getNodeReport`, and `getPipelineReports`.
- Action APIs: `addPipelineActionIfAbsent`, `getPendingPipelineAction`, `addContainerAction`, and `getPendingContainerAction`.
- Command APIs: `addCommand`, `getNextCommand`, `getCommandQueueSummary`, `setTermOfLeaderSCM`, and `getTermOfLeaderSCM`.
- Execution APIs: `execute`, `getTask`, `isThreadPoolAvailable`, and state getters/setters.
- Mock report creation uses protobuf `Message` descriptors and special handling for `IncrementalContainerReportProto`.

## Control Flow
Report tests create contexts with two SCM endpoints, refresh many full reports, add many incremental reports, and assert queue behavior per endpoint. Full reports keep only the latest instance and are sent to each endpoint, while incremental reports are queued and dequeued. `putBackReports` only requeues accepted incremental/report status types for the target endpoint. One flow confirms getting a full container report discards pending ICRs. Action tests add pipeline close actions and container close actions, proving duplicate pipeline actions are suppressed and pipeline actions remain pending until the datanode no longer reports that pipeline. Execution tests create custom `DatanodeState` tasks to ensure shutdown cannot transition back to running, saturated executors prevent execute/await, and awaiting is skipped until thread-pool capacity exists. Command tests count queued command types and validate newer SCM terms advance the context while older-term commands are dropped.

## State And Persistence Behavior
All state is in-memory but central to datanode behavior: per-endpoint report queues, latest full reports, incremental report queues, action queues, command queues, leader SCM term, and current datanode state. No disk persistence is used. Queue draining and requeueing are persistence-like semantics for heartbeat retry reliability.

## Dependencies And Integration Points
The suite integrates with datanode state machine states, protobuf heartbeat report/action types, `OzoneContainer` pipeline reporting, `ContainerSet.getContainerReport`, `SCMCommand` subclasses, executor services, Guava direct executor, and Ozone test waiting utilities. It protects the boundary between report publishers, heartbeat tasks, command handlers, and state-machine transitions.

## Risks And Edge Cases
High-value edge cases include report duplication, lost incremental reports, full container reports not clearing stale ICRs, non-existent endpoints, duplicate pipeline close actions, pipeline action dequeuing before the pipeline is actually gone, restart after shutdown, executor saturation, command summary accuracy, and stale SCM leader-term command rejection.

## Test Signals
Signals are queue count maps by protobuf descriptor name, per-endpoint report availability, action list sizes, executor availability assertions, command type counters, and term/command queue assertions. The tests are mostly mock-based but exercise intricate in-memory control flow.
