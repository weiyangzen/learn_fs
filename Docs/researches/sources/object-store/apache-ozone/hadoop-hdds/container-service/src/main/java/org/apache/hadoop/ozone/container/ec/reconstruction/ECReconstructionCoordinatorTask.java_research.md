# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ec/reconstruction/ECReconstructionCoordinatorTask.java

## Purpose
`ECReconstructionCoordinatorTask` adapts one EC reconstruction command into a runnable replication task understood by the datanode replication supervisor. It supplies metrics naming, deadline/term metadata, status transitions, logging, equality, and delegation to the coordinator.

## Important APIs and Types
It extends `AbstractReplicationTask` and implements `Runnable`. The constructor takes an `ECReconstructionCoordinator` and `ECReconstructionCommandInfo`, passing container ID, deadline, and SCM term to the superclass. It defines metric name `ECReconstructions` and description segment `EC reconstructions`.

## Control Flow
`run()` delegates to `runTask()`. `runTask` logs the command, records a monotonic start time, calls `reconstructECContainerGroup` with container ID, replication config, source map, and target map, then marks status `DONE` on success. It catches any `Exception`, marks status `FAILED`, and logs elapsed time with the failure. `getCommandForDebug` returns a precomputed string from command info.

## State and Persistence
The task itself persists no durable state. In-memory state includes the coordinator reference, command info, debug string, and superclass status/deadline/term fields. Durable effects are performed by the delegated coordinator.

## Dependencies and Integration Points
`ReconstructECContainersCommandHandler` creates this task in response to SCM commands. The replication supervisor schedules it and uses `AbstractReplicationTask` status/metric fields. Tests in `TestReconstructECContainersCommandHandler` verify command handling and metrics name, while `TestReplicationSupervisor` checks scheduling interactions and task de-duplication.

## Risks and Test Signals
Equality and hash code are based only on container ID, so simultaneous reconstruction commands for the same container but different target sets or terms collapse as equal. That is likely intentional for supervisor de-duplication, but it is a risk if SCM ever needs concurrent distinct reconstruction work for the same container. `runTask` catches broad `Exception`, so callers rely on status and logs rather than thrown failures. Tests cover supervisor behavior, but direct task tests for null coordinator misuse and same-container/different-command equality would strengthen coverage.
