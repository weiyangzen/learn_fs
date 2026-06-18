<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestReplicationManagerIntegration.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestReplicationManagerIntegration.java

Purpose: Integration coverage for `ReplicationManager` handling closed-container replica replacement, decommission and maintenance interactions, report generation, and deletion of empty quasi-closed containers.

Important APIs and types: Uses `MiniOzoneCluster`, `NodeManager`, `ContainerManager`, `ReplicationManager`, `ReplicationManagerConfiguration`, `ContainerOperationClient`, `ContainerReplicaCount`, `ReplicationManagerReport`, `ContainerHealthState`, `ContainerReplica`, `ContainerInfo`, `OzoneBucket`, and node operational states including `IN_MAINTENANCE`, `DECOMMISSIONED`, and `IN_SERVICE`.

Control flow: Setup starts five datanodes with fast heartbeat, report, admin-monitor, and replication intervals. Tests create keys, derive container IDs from key locations, close containers, select replica-hosting datanodes, shut down nodes, decommission or maintain nodes through `ContainerOperationClient`, and wait for node state and replica counts. Quasi-closed tests directly create empty replicas with stable or mixed replica states and notify replication manager.

State and persistence behavior: Persistent cluster state includes keys, containers, replica reports, and node operational state. Runtime state includes replication manager queues/reports and container replica sets. The empty quasi-closed paths transition container metadata from `QUASI_CLOSED` to `DELETING` and may update sequence ID from replica BCS IDs.

Dependencies and integration points: Bridges client key writes, SCM container close, node admin commands, dead-node detection, replica-count health logic, command status/report intervals, and replication-manager status checks.

Risks: The tests are timing-sensitive and rely on fast intervals plus repeated waits. Some count assertions intentionally include decommissioned live replicas or extra maintenance-created replicas, so policy changes around replica inclusion will affect them. Empty quasi-closed replica construction bypasses datanode reports and must stay aligned with production replica semantics.

Test signals: Signals include RM thread waiting after notify, closed containers retaining three healthy replicas after dead-node replacement, decommission adding an extra live replica until recommission, maintenance preserving sufficient replication, health report stats at zero for under/mis/over replication, `QUASI_CLOSED` empty containers becoming `DELETING`, and sequence ID updated to max stable replica BCS ID in mixed-state deletion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestReplicationManagerIntegration.java -->
