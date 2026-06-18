# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/ReconcileContainerCommandHandler.java

## Purpose
Handles SCM reconcile-container commands by submitting a reconciliation task that compares and repairs a local container replica against peer replicas.

## Important APIs and Types
Implements `CommandHandler` for `reconcileContainerCommand`. It holds a `ReplicationSupervisor` and `DNContainerOperationClient`. `handle()` creates `ReconcileContainerTask`, while metric methods proxy supervisor counters under `ReconcileContainerTask.METRIC_NAME`.

## Control Flow
The dispatcher invokes `handle()`, which casts the command, constructs a task with the container controller and datanode operation client, and queues it in the supervisor. Actual network checks and repair flow are handled by `ReconcileContainerTask`.

## State and Persistence Behavior
This handler has no durable state. Reconciliation side effects are delegated to the task and container controller. Queue state lives in `ReplicationSupervisor`.

## Dependencies and Integration Points
It integrates with the checksum/reconciliation package, `DNContainerOperationClient`, `OzoneContainer.getController()`, and the shared replication supervisor lane.

## Risks
No local validation beyond cast occurs. Failures and backpressure depend entirely on supervisor/task behavior. It shares supervisor resources with replication and EC tasks, so starvation or queue limits matter outside this file.

## Test Signals
Tests should assert task construction, supervisor submission, command type, metric-name propagation, and queued/invocation/latency values from the supervisor.
