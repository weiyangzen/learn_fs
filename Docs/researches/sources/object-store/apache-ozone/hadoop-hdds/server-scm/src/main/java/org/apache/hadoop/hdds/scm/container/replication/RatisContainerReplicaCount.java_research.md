# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/RatisContainerReplicaCount.java

Purpose: `RatisContainerReplicaCount` is the Ratis implementation of `ContainerReplicaCount`. It summarizes scalar replica counts, pending add/delete counts, state mismatches, maintenance/decommission replicas, and optional unhealthy-replica availability for Ratis health checks and repair handlers.

Important APIs and behavior: constructors accept either raw in-flight counts or `ContainerReplicaOp` lists. The main constructor can `considerUnhealthy`, which affects pending-delete accounting, available replicas, maintenance/decommission counts, and under-replication decisions. `countReplicas` classifies each replica by datanode operational state and replica health. A `QUASI_CLOSED` replica with the wrong sequence ID for a `CLOSED` container is treated as unhealthy.

Control flow: `additionalReplicaNeeded` computes the repair delta using a worst-case model where deletes succeed and adds fail. `missingReplicas` ignores maintenance for over-replication and uses maintenance/decommission counts to decide whether under-replication can be covered by out-of-service replicas while maintaining minimum healthy count. `isSufficientlyReplicated`, `isOverReplicated`, `getExcessRedundancy`, `insufficientDueToOutOfService`, and `getRemainingRedundancy` feed health results. `getVulnerableUnhealthyReplicas` identifies non-empty unhealthy quasi-closed replicas at the container sequence ID whose origins lack an in-service copy.

State and persistence: the object is mostly a derived snapshot, but `getVulnerableUnhealthyReplicas` mutates the internal `replicas` list by removing replicas on non-healthy datanodes. No data is persisted here.

Dependencies and integration: it depends on `ReplicationManager.compareState`, container lifecycle state, replica state, `ContainerReplicaOp`, `NodeStatus`, and datanode operational states. It is used by Ratis health checks, under/over/mis handlers, and datanode admin offline checks.

Risks: the `considerUnhealthy` flag changes semantics significantly; using the wrong count object can cause either missed recovery of only-unhealthy containers or unsafe counting of bad replicas. The mutable list side effect in `getVulnerableUnhealthyReplicas` can surprise callers that reuse the object. Remaining redundancy uses `available + out-of-service - inflight deletes - 1`, so pending delete accuracy is important.

Test signals: `TestRatisContainerReplicaCount` covers pending ops, maintenance minimums, decommission, over/under deltas, mismatched replicas, vulnerable unhealthy replicas, sequence IDs, and offline health checks.
