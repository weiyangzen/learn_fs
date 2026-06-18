<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestReplicationManagerUtil.java -->
## sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestReplicationManagerUtil.java

Purpose: validates `ReplicationManagerUtil.getExcludedAndUsedNodes`, which partitions datanodes into placement-policy used and excluded sets for replication target selection.

Important APIs and types: `ReplicationManagerUtil.ExcludedAndUsedNodes`, `ContainerReplica`, `ContainerReplicaOp`, `NodeStatus`, `NodeManager`, `SCMNodeMetric`, `ContainerReplicaPendingOps.SizeAndTime`, `ReplicationManagerConfiguration`, and `TestClock`.

Control flow: tests build closed or quasi-closed RATIS containers with good, to-be-removed, unhealthy, decommissioning, maintenance, dead-maintenance, pending-add, and pending-delete nodes. The utility is called with replicas, removal candidates, pending ops, and a mocked manager. A disk-space test also stubs scheduled-size maps and node stats to exclude datanodes whose scheduled bytes would violate min free space.

State and persistence behavior: no persistent state. The important mutable state is pending-op scheduled size with timestamps; expired entries should not cause exclusion, while live scheduled bytes can exclude a full target.

Dependencies and integration points: integrates node health/operational state, pending replication/deletion bookkeeping, node capacity metrics, and placement-policy inputs.

Risks: quasi-closed unhealthy replicas are special: a unique origin can remain usable, but a non-unique origin is excluded. Dead maintenance nodes are intentionally neither used nor excluded. Disk-space exclusion depends on timely cleanup of scheduled-size entries.

Test signals: asserts exact used/excluded memberships for normal, quasi-closed, and insufficient-disk-space cases, making this a strong guard for placement candidate filtering.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestReplicationManagerUtil.java -->
