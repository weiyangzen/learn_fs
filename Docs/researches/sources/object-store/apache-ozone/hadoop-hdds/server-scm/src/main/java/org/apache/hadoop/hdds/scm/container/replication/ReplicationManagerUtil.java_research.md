<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ReplicationManagerUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ReplicationManagerUtil.java

## Purpose

`ReplicationManagerUtil` holds shared policy helpers for target selection, used/excluded datanode derivation, scheduled-capacity exclusion, and deterministic unhealthy replica deletion choices. It centralizes rules used by under/over/mis-replication handlers so Ratis and EC processing choose compatible nodes and preserve safety invariants.

## Important APIs, Types, and Functions

Major APIs are `getTargetDatanodes`, `getExcludedAndUsedNodes`, `selectUnhealthyReplicasForDelete`, `selectUnhealthyReplicaForDelete`, and package-visible `findNonUniqueDeleteCandidates`. `ExcludedAndUsedNodes` returns placement inputs. The code depends on `PlacementPolicy`, `ContainerInfo`, `ContainerReplica`, `ContainerReplicaOp`, `ReplicationManager`, `NodeStatus`, and `NodeManager`.

## Control Flow

Target selection calculates required space from the greater of used bytes and default container size, calls the placement policy, and backs off the requested node count until success or zero. Used/excluded derivation walks replicas, treats unhealthy, decommissioning, maintenance-dead, and pending delete/add nodes differently, then excludes nodes whose remaining space minus spare and recent scheduled size cannot hold the container. Unhealthy deletion selection first refuses unsafe cases, sorts candidates by sequence ID, and for quasi-closed containers only returns candidates whose origin IDs are not uniquely represented by valid replicas.

## State and Persistence Behavior

The class owns no persistent state. It reads transient pending-op scheduled-size maps, node status/statistics, container metadata, and replica sets. Deterministic ordering matters because leaders can change; deletion choices should remain stable across SCMs when inputs match.

## Dependencies and Integration Points

It integrates with placement policy validation/selection, pending replica ops, SCM node metrics, maintenance/decommission state, and `ReplicationManager.compareState`. It is called by replication handlers that issue commands and by quasi-closed unhealthy cleanup logic.

## Risks and Edge Cases

The logic deliberately avoids deleting when there are pending deletes, when too few replicas remain, or when no replica matches container state. Node-not-found and null node-status paths bias toward exclusion or no deletion. Scheduled-size exclusion only considers entries newer than the event timeout, so stale pending sizes are ignored. Origin uniqueness is subtle and protects data in quasi-closed containers.

## Test Signals

Tests should cover placement backoff, detailed used/excluded classification for unhealthy/decommission/maintenance/dead/pending ops, full-node exclusion with scheduled sizes, closed versus quasi-closed deletion candidate ordering, non-unique origin preservation, node-not-found fallbacks, and deterministic behavior under reordered sets where sorting is expected.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ReplicationManagerUtil.java -->
