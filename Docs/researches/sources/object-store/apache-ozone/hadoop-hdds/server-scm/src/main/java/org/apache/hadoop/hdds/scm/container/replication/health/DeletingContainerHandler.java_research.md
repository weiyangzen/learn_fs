<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/DeletingContainerHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/DeletingContainerHandler.java

## Purpose

`DeletingContainerHandler` handles containers in `DELETING` or `DELETED` state. It marks replica-free deleting containers for cleanup and resends delete commands for empty replicas that are not already covered by pending delete ops.

## Important APIs, Types, and Functions

The main method is `handle`. It uses `ReplicationManager.updateContainerState`, `ReplicationManager.sendDeleteCommand`, `LifeCycleEvent.CLEANUP`, pending-op type `DELETE`, `ContainerReplica.isEmpty`, and `NotLeaderException`.

## Control Flow

Already deleted containers return handled. Non-deleting containers pass through. Read-only deleting containers return handled without mutation. If no replicas exist, the handler emits the cleanup lifecycle event. Otherwise it builds the pending-delete datanode set and sends delete commands for empty replicas not already pending.

## State and Persistence Behavior

It changes persistent SCM lifecycle state through `updateContainerState` and schedules transient delete commands. Replica deletion completion later removes container replica state.

## Dependencies and Integration Points

It integrates with pending ops, datanode command sending, lifecycle state manager, and the health chain to prevent normal replication repairs for deleting containers.

## Risks and Edge Cases

Only empty replicas are resent delete commands, so non-empty replicas in deleting state are not force-deleted by this handler. Not-leader failures are logged. Duplicate pending deletes are avoided by datanode matching.

## Test Signals

Tests should cover deleted pass-through, deleting no-replica cleanup, read-only no mutation, resend for empty replica without pending delete, suppression when pending delete exists, non-empty replica skip, and not-leader handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/DeletingContainerHandler.java -->
