# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/checksum/ReconcileContainerTask.java

## Purpose
Replication-supervisor task that executes one queued container reconciliation command.

## Important APIs, Types, And Functions
Extends `AbstractReplicationTask`, stores `ReconcileContainerCommand`, `DNContainerOperationClient`, and `ContainerController`, and overrides `runTask`, `getCommandForDebug`, metric name/description, `equals`, and `hashCode`.

## Control Flow
When run, it logs the task, calls `controller.reconcileContainer` with the client, container ID, and peer datanodes from the command, marks status `DONE` on success, or `FAILED` on any exception, logging elapsed time either way.

## State And Persistence
State is the command, controller/client references, inherited deadline/term/status, and no durable persistence.

## Dependencies And Integration Points
Integrates with replication supervisor scheduling, container controller repair logic, reconciliation commands from SCM, and task metrics.

## Risks
Catching all exceptions prevents task crashes but collapses all failure causes into `FAILED`. Equality compares command while hash code uses container ID, which is acceptable only if command equality is container-centric enough for sets/maps.

## Test Signals
Signals include status transitions, metric name aggregation, deadline handling inherited from the base task, successful controller invocation, failure logging, and duplicate-task behavior in supervisor collections.
