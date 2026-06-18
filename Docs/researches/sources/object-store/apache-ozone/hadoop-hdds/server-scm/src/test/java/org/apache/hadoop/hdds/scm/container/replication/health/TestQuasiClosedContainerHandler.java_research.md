<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestQuasiClosedContainerHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestQuasiClosedContainerHandler.java

Purpose: This suite validates `QuasiClosedContainerHandler`, which force-closes eligible Ratis `QUASI_CLOSED` containers once enough safe replicas exist. It explicitly excludes EC and open containers.

Important APIs and types: The tests use `QuasiClosedContainerHandler`, `ReplicationManager.sendCloseContainerReplicaCommand`, `ContainerCheckRequest`, `ReplicationManagerReport`, `ContainerHealthState.QUASI_CLOSED_STUCK`, `RatisReplicationConfig`, `ContainerReplica`, and `HddsTestUtils.getContainer/getReplicas` helpers for precise sequence ID and origin-node construction.

Control flow: Setup creates a mocked `ReplicationManager` and handler. Non-Ratis and open containers return false. Quasi-closed containers with insufficient unique origins, duplicate origins, or open replicas are not force-closed and may be counted as stuck. Containers with all unique origins and equal highest BCSID send close commands for eligible replicas. Read-only requests re-run the logic but do not add additional commands.

State and persistence behavior: The suite is memory-only. State under test is replica state, BCSID/sequence ID, origin datanode ID uniqueness, datanode identity, and the request read-only flag.

Dependencies and integration points: It anchors the Replication Manager interaction that sends close-replica commands to datanodes and protects the Ratis-only semantics used before regular under/over replication repair.

Risks: Eligibility depends on subtle BCSID and origin rules. A replica with the highest sequence ID but `UNHEALTHY` state can prevent force close, while only highest-BCSID quasi-closed replicas should receive commands.

Test signals: Assertions verify no command for EC/open/stuck cases, report increments for stuck cases, command counts for all-unique cases, and exact datanodes selected when only some replicas have the highest BCSID.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestQuasiClosedContainerHandler.java -->
