# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/TestContainerReportHandlingWithHA.java

Purpose: This is the SCM HA counterpart to `TestContainerReportHandling`. It verifies that leader-driven deletion handling for `DELETING` or `DELETED` containers works when the cluster has multiple StorageContainerManagers and the closed state must be visible on every SCM before deletion is driven.

Important APIs and types: It uses `MiniOzoneHAClusterImpl`, `MiniOzoneCluster.newHABuilder`, `StorageContainerManager`, `ContainerManager`, `ContainerID`, `ReplicationConfig`, `TestHelper.ReplicationInput`, `waitForContainerClose`, `waitForContainerStateInSCM`, `HddsProtos.LifeCycleState`, `HddsProtos.LifeCycleEvent`, and the same OM lookup types used by the non-HA test.

Control flow: The parameter source crosses desired final deletion state with RATIS and EC replication. The test creates a three-SCM HA cluster with one OM and enough datanodes for the selected replication. After writing and closing a key container, it calls `waitForContainerStateInAllSCMs` to ensure every SCM has the closed container state. It then updates the leader's `ContainerManager` through `DELETE` and optional `CLEANUP`, restarts all datanodes that host the key, and waits until the leader's replica set for the container is empty.

State and persistence behavior: The test stresses replicated SCM metadata and leader state. Container lifecycle state is expected to be present on all SCMs before the delete transition. Replica tracking is then validated on the leader after reports from restarted datanodes. Like the non-HA version, it cleans the cluster base directory manually in `finally`.

Dependencies and integration points: This covers HA builder configuration, SCM leader access via `cluster.getScmLeader()`, OM key metadata, datanode full container reports, and HA propagation of container lifecycle state. The helper method iterates `cluster.getStorageContainerManagersList()` to avoid asserting delete behavior before followers have observed closure.

Risks: The test does not explicitly fail over the SCM leader, so it covers HA state propagation but not leader change during deletion. It assumes the current leader remains valid while commands are scheduled. Timing is similar to the non-HA test and can be affected by report intervals and HA transaction flush latency.

Test signals: Strong signals include closed state observed on all SCMs, exact leader state after `DELETE` and optional `CLEANUP`, datanode restarts for all replica hosts, and eventual empty leader-side replica records for both RATIS and EC replication inputs.
