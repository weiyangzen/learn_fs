# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestReconstructECContainersCommandHandler.java

## Purpose
`TestReconstructECContainersCommandHandler` verifies metrics and task-submission behavior for EC container reconstruction commands.

## Important APIs, Types, And Functions
- `ReconstructECContainersCommandHandler.handle`, `getCommandType`, `getMetricsName`, `getInvocationCount`, `getQueuedCount`, `getTotalRunTime`, and `getAverageRunTime` are tested.
- `ReconstructECContainersCommand` carries container ID, source datanodes with replica indexes, target datanodes, missing indexes, and `ECReplicationConfig`.
- `ReplicationSupervisor.addTask` is the handoff to execution.
- `CommandHandlerMetrics.create` exposes metrics for command handlers.

## Control Flow
Setup creates mocked supervisor, EC coordinator, Ozone container, state context, and connection manager. The test builds a command with EC 3-2 replication, five sources, two targets, and missing indexes. It handles one command, asserts the metric name matches `ECReconstructionCoordinatorTask.METRIC_NAME`, stubs supervisor request count to one, and checks invocation count. It then handles five more commands, stubs supervisor counters, and verifies capped/derived handler metrics and that the metrics collector emits one record.

## State And Persistence Behavior
No persistent state is used. Handler state is metrics/invocation accounting; actual reconstruction work is delegated and mocked.

## Dependencies And Integration Points
Dependencies include EC replication config, protobuf `ByteString` for missing indexes, `ECReconstructionCoordinator`, `ReplicationSupervisor`, `CommandHandlerMetrics`, and SCM command types. It protects metrics integration for reconstruction work.

## Risks And Edge Cases
Covered risks include wrong metric name, missing task submission, metrics not reflecting supervisor counters, and metrics source not registering records. It does not validate reconstruction data movement.

## Test Signals
Signals are invocation counts, queued/total/average runtime values, metric-name equality, and metrics collector record count.
