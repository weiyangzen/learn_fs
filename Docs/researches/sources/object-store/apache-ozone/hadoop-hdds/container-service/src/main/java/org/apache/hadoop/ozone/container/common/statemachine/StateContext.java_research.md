# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/StateContext.java

## Purpose
`StateContext` is the mutable runtime context shared by the datanode state machine, endpoint tasks, report publishers, and command processing. It tracks datanode state, queued SCM commands, full and incremental reports, container and pipeline actions, command status, endpoint-specific queues, heartbeat intervals, and leader SCM term filtering.

## Important APIs and Types
Core APIs include `execute()`, `getTask()`, `addCommand()`, `getNextCommand()`, `refreshFullReport()`, `addIncrementalReport()`, `getAllAvailableReports()`, `putBackReports()`, `addContainerActionIfAbsent()`, `getPendingContainerAction()`, `addPipelineActionIfAbsent()`, `getPendingPipelineAction()`, command-status methods, endpoint add/remove methods, heartbeat frequency configuration, and queue-size accessors. Nested `PipelineActionMap` and `PipelineKey` deduplicate and retain close-pipeline actions until the local pipeline disappears.

## Control Flow
`DatanodeStateMachine` calls `execute()` each heartbeat cycle. The context creates the correct state task (`InitDatanodeState` or cached `RunningDatanodeState`), invokes enter/execute/await/exit hooks, enforces executor availability, advances allowed states, and marks fatal shutdown when a non-graceful task returns `SHUTDOWN`. Reports are drained per endpoint by heartbeat tasks: full reports are controlled by per-endpoint ready flags, and incremental reports are removed as returned.

## State and Persistence Behavior
Most state is process memory. Command statuses for delete-block commands are retained in `cmdStatusMap` so heartbeat reports can return ACKs. The leader SCM term is initialized after a majority of active SCM endpoints reach heartbeat state and commands are available, then stale-term commands are dropped. Full reports keep only the latest message per type; incremental reports and actions are endpoint-specific queues.

## Dependencies and Integration Points
It integrates with `DatanodeStateMachine`, `SCMConnectionManager`, `RunningDatanodeState`, `InitDatanodeState`, report manager publishers, endpoint heartbeat/register/version tasks, `OzoneContainer`, `ClosePipelineCommandHandler`, and protobuf report/action/command types.

## Risks
Concurrency is mixed: a `ReentrantLock` protects command queue operations, some maps are synchronized manually, some are concurrent, and endpoint sets are unsynchronized in some paths. Full report ready flags must be maintained for every endpoint and report type. Leader-term initialization delays command processing until majority heartbeat conditions are met, which is correct for HA but can look like a stalled queue if endpoints do not advance.

## Test Signals
Tests should cover state transitions, task lifecycle hooks, executor-unavailable warnings, report drain and put-back ordering, full-report ready flags, ICR discard during full container reports, endpoint queue initialization/removal, command queue limits, stale leader-term filtering, command status updates, and pipeline action deduplication/retention.
