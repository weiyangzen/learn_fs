<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestVulnerableUnhealthyReplicasHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestVulnerableUnhealthyReplicasHandler.java

Purpose: This suite validates `VulnerableUnhealthyReplicasHandler`, which tries to save unhealthy quasi-closed Ratis replicas that are on vulnerable operational-state nodes and represent a unique origin copy worth preserving.

Important APIs and types: It uses `VulnerableUnhealthyReplicasHandler`, mocked `ReplicationManager.getNodeStatus`, `NodeStatus`, `ReplicationQueue`, `ContainerCheckRequest`, `RatisReplicationConfig`, `ECReplicationConfig`, and `ReplicationTestUtil.createContainerReplica` overloads for sequence ID and origin control.

Control flow: The handler ignores EC containers, closed containers, quasi-closed containers with no unhealthy replicas, and unhealthy replicas that are not vulnerable because another replica has the same origin. It queues under-replication for an unhealthy replica on a decommissioning node when that replica has a unique origin and correct sequence ID, even if the quasi-closed replicas have correct sequence IDs. A read-only request still returns true for detection but does not enqueue work.

State and persistence behavior: All state is in memory: container lifecycle state, replica states, sequence IDs, origins, datanode operational status, read-only flag, and queue contents.

Dependencies and integration points: The test guards the interaction between container health checking and Replication Manager's node status service. It is specifically about preserving quorum/recovery options for quasi-closed containers during decommission-like transitions.

Risks: The value of an unhealthy replica depends on origin uniqueness, not just count. A naive repair path could delete or ignore a vulnerable unique-origin copy before it can be restored or used for closure.

Test signals: Signals are zero queues for ignored cases, one under-replication queue entry for vulnerable unique-origin unhealthy replicas, mocked node-status branching, and no queue entry for read-only detection.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestVulnerableUnhealthyReplicasHandler.java -->
