<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/RatisReplicationCheckHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/RatisReplicationCheckHandler.java

## Purpose

`RatisReplicationCheckHandler` is the main health classifier for Ratis containers. It detects under-replication, over-replication, mis-replication, missing containers, and containers with excess unhealthy replicas while deferring special all-unhealthy and quasi-closed-stuck cases to other handlers.

## Important APIs, Types, and Functions

Important methods are `handle`, `checkHealth`, and private `getPlacementStatus`. It uses `RatisContainerReplicaCount`, `PlacementPolicy`, `ReplicationManagerUtil.selectUnhealthyReplicaForDelete`, `ContainerHealthResult` subclasses, and report states `MISSING`, `UNDER_REPLICATED`, `OVER_REPLICATED`, and `MIS_REPLICATED`.

## Control Flow

The handler ignores non-Ratis containers and quasi-closed-stuck containers. `checkHealth` first checks sufficient replication without counting unhealthy replicas; if insufficient it returns under health. It checks over-replication without unhealthy replicas, then over-replication while considering unhealthy replicas. For quasi-closed over-replication, it only reports over-replicated if a safely deletable unhealthy replica exists. Finally it validates placement policy after pending ops and returns unhealthy or healthy if no other issue exists. `handle` samples reports and enqueues only when pending ops are insufficient and safety flags allow.

## State and Persistence Behavior

It owns no persistent state. It reads replicas, pending ops, maintenance redundancy, and node status through ReplicationManager. It mutates report samples and replication queues only.

## Dependencies and Integration Points

It integrates with placement policy, ReplicationQueue, Ratis replica-count logic, ReplicationManager node status, quasi-closed stuck checks, and later under/over/mis-replication processors.

## Risks and Edge Cases

Counting unhealthy replicas differently for under versus over checks is intentional and subtle. A recoverable container with no healthy replicas is left for unhealthy replication checks. Mismatched replicas suppress over-replication queueing until close commands can converge state.

## Test Signals

Tests should cover under-replication without unhealthy counting, over-replication with and without unhealthy replicas, quasi-closed unique-origin preservation, missing/unrecoverable classification, pending-op queue suppression, mis-replication placement reasons, mismatched-replica queue suppression, and special stuck pass-through.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/RatisReplicationCheckHandler.java -->
