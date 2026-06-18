# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestReplicateContainerCommandHandler.java

## Purpose
`TestReplicateContainerCommandHandler` verifies metrics and task-submission accounting for container replication commands, including both pull-from-sources and push-to-target command forms.

## Important APIs, Types, And Functions
- `ReplicateContainerCommandHandler.handle`, `getCommandType`, `getMetricsName`, `getInvocationCount`, `getQueuedCount`, `getTotalRunTime`, and `getAverageRunTime` are under test.
- `ReplicateContainerCommand.fromSources` and `toTarget` create download and push replication commands.
- `ReplicationSupervisor.addTask` accepts replication tasks.
- `ContainerReplicator` mocks represent download and push implementations.
- `CommandHandlerMetrics.create` registers metrics for the handler map.

## Control Flow
The test creates a handler with mocked supervisor and replicators, registers command metrics, and sends one source-based command to check metric name and initial invocation count. It then sends additional source-based and target-based commands, stubs supervisor metrics for `ReplicationTask.METRIC_NAME`, and asserts invocation count, queued count, total runtime, average runtime, and that metrics collection produces one record.

## State And Persistence Behavior
No container data is persisted. The test validates handler accounting and delegation state only.

## Dependencies And Integration Points
Dependencies include `ReplicationSupervisor`, `ContainerReplicator`, `ReplicationTask`, `CommandHandlerMetrics`, Ozone command models, and SCM command type registration. It protects metrics integration for replication work regardless of direction.

## Risks And Edge Cases
Covered risks include metrics name drift, push commands not counted with source commands, supervisor metrics not surfacing through the handler, and metrics source registration issues.

## Test Signals
Signals include invocation count, supervisor-derived queued/runtime metrics, and metrics collector record count.
