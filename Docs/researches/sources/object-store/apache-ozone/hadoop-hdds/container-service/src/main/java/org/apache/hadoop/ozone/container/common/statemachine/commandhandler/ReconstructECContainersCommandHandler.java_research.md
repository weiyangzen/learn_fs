# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/ReconstructECContainersCommandHandler.java

## Purpose
Handles SCM EC reconstruction commands by submitting erasure-coded reconstruction tasks to the replication supervisor.

## Important APIs and Types
Implements `CommandHandler` for `reconstructECContainersCommand`. It stores `ConfigurationSource`, `ReplicationSupervisor`, and `ECReconstructionCoordinator`. `handle()` creates `ECReconstructionCommandInfo` and `ECReconstructionCoordinatorTask`. Metrics proxy supervisor values using `ECReconstructionCoordinatorTask.METRIC_NAME`.

## Control Flow
Command dispatch synchronously creates the reconstruction task and queues it with the supervisor. EC reconstruction execution, downloads, reconstruction, and writes are performed by the coordinator task outside this handler.

## State and Persistence Behavior
No durable state is written directly. Reconstruction task execution can create or repair EC container replicas via the coordinator.

## Dependencies and Integration Points
It integrates with `ECReconstructionCoordinator`, `ECReconstructionCommandInfo`, `ReplicationSupervisor`, and SCM EC command protobuf wrappers. The state machine constructs it once so tests can mock it in mini-cluster scenarios.

## Risks
No validation or queue handling is local; all backpressure and failures are supervisor-level. Reconstruction can be resource-heavy, so metrics and queue counts are important operational signals.

## Test Signals
Tests should verify command casting, task submission, metric proxy values, config accessor, and behavior under supervisor queue saturation if applicable.
