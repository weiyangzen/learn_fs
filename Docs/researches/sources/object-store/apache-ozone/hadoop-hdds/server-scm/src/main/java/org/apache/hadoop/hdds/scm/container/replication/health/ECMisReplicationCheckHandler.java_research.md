<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/ECMisReplicationCheckHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/ECMisReplicationCheckHandler.java

## Purpose

`ECMisReplicationCheckHandler` detects EC containers whose replica datanodes do not satisfy placement policy even though the container is not under/over replicated. It queues mis-replication repairs when pending ops will not already fix placement.

## Important APIs, Types, and Functions

Key methods are `handle`, `checkMisReplication`, and private `getPlacementStatus`. It uses `PlacementPolicy.validateContainerPlacement`, `ContainerHealthResult.MisReplicatedHealthResult`, and `ContainerHealthState.MIS_REPLICATED`.

## Control Flow

The handler ignores non-EC containers. It validates placement from current replica datanodes. If placement fails, it revalidates after applying pending add/delete ops to a datanode set. It reports mis-replication and enqueues only when pending ops do not satisfy placement.

## State and Persistence Behavior

It owns no state. It samples the report and enqueues transient repair work. Placement state is computed from current replicas and pending ops.

## Dependencies and Integration Points

It integrates with the EC health chain after replication-count checks, placement policy, ReplicationManager queue, and mis-replication repair handlers.

## Risks and Edge Cases

It uses datanode uniqueness, not EC index counts, so it assumes earlier EC replication checks handled missing/excess indexes. Pending-op application removes/introduces datanodes without validating command success.

## Test Signals

Tests should verify non-EC pass-through, placement satisfied pass-through, current placement failure with pending add fix not queued, pending delete worsening placement, report increment, queued `MisReplicatedHealthResult`, and reason propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/ECMisReplicationCheckHandler.java -->
