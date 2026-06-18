<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/UnhealthyReplicationHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/UnhealthyReplicationHandler.java

## Purpose

`UnhealthyReplicationHandler` is the command-generation interface for handlers that repair unhealthy, under-replicated, over-replicated, or mis-replicated containers after health checks classify them.

## Important APIs, Types, and Functions

The single method `processAndSendCommands` receives available replicas, pending ops, a `ContainerHealthResult`, and remaining maintenance redundancy, then returns the number of commands sent. It may throw `IOException`.

## Control Flow

Implementations inspect current replicas and inflight operations, compute required add/delete/reconstruct actions, send SCM commands to selected datanodes, and update pending-op tracking. This interface has no implementation flow itself.

## State and Persistence Behavior

It owns no state. Implementations affect transient pending ops and eventually persistent SCM/container state through command completion reports and container metadata updates.

## Dependencies and Integration Points

It links health classification output to concrete datanode commands. Implementations depend on `ContainerReplica`, `ContainerReplicaOp`, `ContainerHealthResult`, placement policy, node manager state, and ReplicationManager command APIs.

## Risks and Edge Cases

Callers assume command counts reflect actual scheduled work. Implementations must account for pending adds/deletes, maintenance redundancy, overloaded targets, and read-after-classification drift in replica sets.

## Test Signals

Interface-level signals are implementation tests asserting command counts, pending-op mutations, handling of maintenance/decommission replicas, and expected exceptions for placement or overloaded-target failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/UnhealthyReplicationHandler.java -->
