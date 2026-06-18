<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/VulnerableUnhealthyReplicasHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/VulnerableUnhealthyReplicasHandler.java

## Purpose

`VulnerableUnhealthyReplicasHandler` protects quasi-closed Ratis containers whose unhealthy replicas may contain unique or highest-sequence data. It queues under-replication work to copy such vulnerable replicas before they are lost.

## Important APIs, Types, and Functions

The main method is `handle`. It builds `RatisContainerReplicaCount` considering unhealthy replicas, calls `getVulnerableUnhealthyReplicas`, reports `UNHEALTHY_UNDER_REPLICATED`, and enqueues an `UnderReplicatedHealthResult` marked with `setHasVulnerableUnhealthy(true)`.

## Control Flow

The handler ignores non-Ratis and non-quasi-closed containers. It asks `ReplicationManager.getNodeStatus` for datanode health while calculating vulnerability. If vulnerable unhealthy replicas exist, it samples the report and, unless read-only, queues under-replication work that downstream handlers can interpret as vulnerable-unhealthy repair.

## State and Persistence Behavior

It owns no state. Node status and replica sets are read at scan time. Persistent effects occur only later if queued work produces copy commands and those commands complete.

## Dependencies and Integration Points

It integrates with `RatisContainerReplicaCount`, ReplicationManager node status, ReplicationQueue, and quasi-closed recovery logic.

## Risks and Edge Cases

Node-not-found is logged and treated as null status by the vulnerability calculation. Read-only scans report without queueing. Incorrect vulnerability detection can either lose rare data or create unnecessary copies.

## Test Signals

Tests should cover vulnerable unique-origin or high-sequence unhealthy replicas, no-vulnerability pass-through, node-not-found fallback, read-only queue suppression, report sampling, and queued under-health result carrying the vulnerable flag.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/VulnerableUnhealthyReplicasHandler.java -->
