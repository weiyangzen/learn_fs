# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestRatisOverReplicationHandler.java

Purpose: Tests `RatisOverReplicationHandler`, which chooses safe replicas to delete from over-replicated Ratis containers while respecting placement, replica state, origin preservation, pending deletes, and throttling.

Important APIs and types: Uses `RatisOverReplicationHandler`, `RatisReplicationConfig`, `ContainerHealthResult.OverReplicatedHealthResult`, `PlacementPolicy`, `ContainerPlacementStatusDefault`, `ContainerReplica`, `ContainerReplicaOp`, `DeleteContainerCommand`, `NodeStatus`, and command throttling.

Control flow: Setup creates a closed Ratis container, placement policy mock, healthy node-status mock, and delete command capture. Tests cover closed over-replication with pending delete, stale node exclusion, quasi-closed containers with same vs different origins, all-unhealthy and excess-unhealthy handling, placement-aware deletion that avoids making placement worse, deletion when already mis-replicated but not worsened, staged deletion stopping before second removal breaks placement, all-unhealthy deterministic selection by BCSID/hash, deleting mismatched quasi-closed replicas from closed containers, avoiding decommissioning/maintenance replicas as delete candidates, perfect replication, wrong-sequence quasi-closed behavior, and throttling.

State and persistence behavior: In-memory replica sets encode state, op-state, origin, and sequence ID. Pending delete ops reduce excess. Placement validation controls whether deletion is safe. Commands are captured rather than persisted.

Dependencies and integration points: Integrates with placement-policy validation, node status, `ReplicationManager.sendThrottledDeleteCommand`, Ratis container state semantics, and command retry behavior after `CommandTargetOverloadedException`.

Risks and test signals: Risks include deleting unique-origin quasi-closed replicas, worsening placement, deleting decommission/maintenance replicas prematurely, selecting high-BCSID unhealthy replicas before lower-BCSID ones, or continuing too far after throttling. Signals are exact command counts, target datanode assertions, placement mock behavior, exception assertions, and command type/index checks.
