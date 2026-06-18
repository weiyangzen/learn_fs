<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/ClosedWithUnhealthyReplicasHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/ClosedWithUnhealthyReplicasHandler.java

## Purpose

This handler deletes extra unhealthy replicas from closed EC containers after normal EC under/over checks have determined the container is otherwise sufficiently replicated by closed indexes.

## Important APIs, Types, and Functions

The main method is `handle`. The helper `sendDeleteCommand` calls `ReplicationManager.sendDeleteCommand(container, replicaIndex, datanode, true)`. It uses EC `ReplicationType`, `LifeCycleState.CLOSED`, replica states, and `ContainerHealthState.UNHEALTHY_OVER_REPLICATED`.

## Control Flow

The handler ignores non-EC and non-closed containers. It gathers indexes with closed replicas, scans unhealthy replicas, and refuses to handle if an unhealthy index has no closed counterpart because that index is actually under-replicated. Otherwise it samples the report and, unless read-only, sends force delete commands for unhealthy replicas.

## State and Persistence Behavior

It owns no state except the ReplicationManager reference. Side effects are pending delete commands and report samples. Persistent metadata changes happen later when delete commands complete.

## Dependencies and Integration Points

It integrates with EC health checks, ReplicationManager command sending, `NotLeaderException` handling, and report classification. It is intended to run after under/over replication detection so it does not mask missing EC indexes.

## Risks and Edge Cases

Incorrect chain order could delete an unhealthy replica when no healthy index exists. Read-only mode records classification without commands. Not-leader failures are logged and not retried here.

## Test Signals

Tests should cover closed EC with duplicate unhealthy index deletion, unhealthy index without closed counterpart returning false, non-EC/non-closed pass-through, read-only no command, report increment, and not-leader logging behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/ClosedWithUnhealthyReplicasHandler.java -->
