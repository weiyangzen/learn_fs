<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/EmptyContainerHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/EmptyContainerHandler.java

## Purpose

`EmptyContainerHandler` deletes closed or quasi-closed containers whose replicas are empty. It prevents empty containers from being treated as missing or under-replicated and handles quasi-closed empty deletion carefully to preserve resurrection sequence semantics.

## Important APIs, Types, and Functions

Important methods are `handle`, `isContainerEmptyAndClosed`, `isContainerEmptyAndQuasiClosed`, and `deleteContainerReplicas`. It uses `ContainerHealthState.EMPTY`, `LifeCycleEvent.DELETE`, `sendDeleteCommand`, `ContainerReplica.isEmpty`, and sequence-id updates.

## Control Flow

For closed containers, all replicas must be closed and empty; delete commands are sent and the container moves to deleting, except Ratis closed containers whose replica sequence IDs do not match the container sequence ID. For quasi-closed containers, all replicas must be empty regardless of state; the container BCSID is raised to the max replica BCSID if needed, SCM state moves to deleting, and delete commands are sent only to closed or quasi-closed replicas. Closed empty containers with no replicas are reported as empty but not deleted.

## State and Persistence Behavior

It mutates container sequence ID in memory before lifecycle update when quasi-closed replicas have a higher BCSID. It schedules delete commands and updates persistent lifecycle state through ReplicationManager. It does not inspect used bytes because orphaned chunks can make it misleading.

## Dependencies and Integration Points

It integrates with ReplicationManager lifecycle updates, delete commands, health reports, and resurrection/stale replica logic that depends on BCSID.

## Risks and Edge Cases

Deleting empty quasi-closed containers before all replicas reach stable states can leave open/closing replicas for a later retry. Closed Ratis sequence mismatch suppresses state transition. Preconditions assert replicas are empty before deletion.

## Test Signals

Tests should verify closed-empty deletion, quasi-closed empty deletion and BCSID update, skip of unstable replica delete commands, no-replica closed empty report-only path, Ratis sequence mismatch suppression, read-only no mutation, and report sampling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/EmptyContainerHandler.java -->
