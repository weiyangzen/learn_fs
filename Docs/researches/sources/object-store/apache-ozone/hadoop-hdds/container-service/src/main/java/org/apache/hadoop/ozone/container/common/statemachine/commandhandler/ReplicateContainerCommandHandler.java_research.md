# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/ReplicateContainerCommandHandler.java

## Purpose
Handles SCM replicate-container commands by creating a replication task using either pull/download replication or push/upload replication.

## Important APIs and Types
Implements `CommandHandler` for `replicateContainerCommand`. It stores a `ReplicationSupervisor`, a download `ContainerReplicator`, a push `ContainerReplicator`, and proxies metrics under `ReplicationTask.METRIC_NAME`.

## Control Flow
`handle()` casts the command, reads source datanodes, target datanode, and container ID, validates that at least sources or target exist, picks pull replication when target is null or push replication when target is present, creates `ReplicationTask`, and adds it to the supervisor.

## State and Persistence Behavior
The handler has no durable state. Actual container import/export and metadata changes happen inside the selected replicator and task.

## Dependencies and Integration Points
It integrates with `ReplicationSupervisor`, `ReplicationTask`, pull and push `ContainerReplicator` implementations, and SCM replication commands. It shares supervisor capacity with EC reconstruction and reconciliation tasks.

## Risks
Invalid commands throw `IllegalArgumentException`, which is caught by the dispatcher and logged. Replicator selection depends only on target presence, so command semantics must remain consistent. Queue pressure is external to this handler.

## Test Signals
Tests should verify pull vs push selection, precondition failure for missing sources and target, supervisor task submission, metric proxy values, and command type registration.
