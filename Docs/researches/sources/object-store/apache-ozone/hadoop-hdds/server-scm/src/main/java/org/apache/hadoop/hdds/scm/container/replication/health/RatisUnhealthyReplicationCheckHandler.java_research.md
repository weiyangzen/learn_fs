<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/RatisUnhealthyReplicationCheckHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/RatisUnhealthyReplicationCheckHandler.java

## Purpose

`RatisUnhealthyReplicationCheckHandler` handles Ratis containers that have no healthy replicas but do have unhealthy or stale quasi-closed-style replicas. It maintains the expected replication factor of those unhealthy replicas instead of immediately declaring only missing.

## Important APIs, Types, and Functions

Important methods are `handle`, testing-visible `checkReplication(ContainerCheckRequest)`, private `getReplicaCount`, and private `checkReplication(RatisContainerReplicaCount)`. It reports `UNHEALTHY_UNDER_REPLICATED`, `UNHEALTHY_OVER_REPLICATED`, or `UNHEALTHY`.

## Control Flow

The handler ignores non-Ratis containers and containers with any healthy replica or no unhealthy replicas. It constructs `RatisContainerReplicaCount` with unhealthy replicas considered. It returns under health if insufficient, over health if excessive, or unhealthy if sufficiently replicated. Under/over results are reported and queued when pending ops do not already fix them.

## State and Persistence Behavior

It owns no state. It samples reports and enqueues repair results. Actual replication/delete commands are produced later by processors.

## Dependencies and Integration Points

It integrates with Ratis replica-count calculations, ReplicationQueue, and the health chain after the main Ratis replication check declines recoverable no-healthy-replica cases.

## Risks and Edge Cases

It returns `false` after reporting sufficiently replicated unhealthy containers, allowing later handlers to continue. Because all healthy replicas are absent, repair commands must avoid assuming a clean source unless downstream handlers explicitly support unhealthy replication.

## Test Signals

Tests should cover no healthy replicas under/over/sufficient cases, pending-op fix suppression, report state selection, queueing behavior, pass-through when healthy replicas exist, and pass-through when no unhealthy replicas exist.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/RatisUnhealthyReplicationCheckHandler.java -->
