<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/node/TestDecommissionAndMaintenance.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/node/TestDecommissionAndMaintenance.java

Purpose: End-to-end tests for SCM datanode decommission and maintenance workflows across Ratis and EC containers, including open pipeline closure, replica creation/removal, SCM restart recovery, insufficient-node validation, maintenance expiry, and persisted datanode state.

Important APIs and types: Uses `MiniOzoneClusterProvider`, `StorageContainerManager`, `NodeManager`, `ContainerManager`, `PipelineManager`, `ContainerOperationClient`, `ReplicationManagerConfiguration`, `ContainerReplicaCount`, `RatisReplicationConfig`, `ECReplicationConfig`, `ContainerInfo`, `ContainerReplica`, `Pipeline`, and `TestNodeUtil` wait helpers.

Control flow: A shared provider supplies seven-datanode clusters with shortened heartbeat/report/admin-monitor intervals. Each test creates keys to force containers, finds containers and replica-hosting nodes, issues decommission or maintenance commands, waits for `DECOMMISSIONING`, `DECOMMISSIONED`, `ENTERING_MAINTENANCE`, `IN_MAINTENANCE`, or `IN_SERVICE`, restarts SCM or datanodes, and validates replica counts. Helpers generate data, fetch replica sets, choose a replica-hosting DN, stop replication manager, and wait for exact replica counts.

State and persistence behavior: The suite heavily tests persisted node operational state in `DatanodeDetails`, SCM's node status, container replica sets, pipeline states, and container metadata across SCM and datanode restarts. Maintenance expiry is injected by setting node operational state with an end timestamp. Dead maintenance nodes can retain or lose replicas depending on restart timing.

Dependencies and integration points: Integrates SCM admin CLI client, datanode heartbeat/report loops, pipeline manager, replication manager, OM/Ozone key writes, EC and Ratis placement requirements, SCM decommission monitor, and cluster restart behavior.

Risks: The tests are long-running and rely on asynchronous state convergence. The provider reuses clusters, so `tearDown` must destroy supplied clusters. Several checks are policy-sensitive, especially required remaining nodes for EC, maintenance redundancy, and whether dead maintenance replicas are purged after SCM restart.

Test signals: Signals include decommissioned nodes reaching persisted state, Ratis replica counts moving 3 to 4 to 3 and EC 5 to 6 to 5, stuck decommission completing after SCM restart, insufficient non-forced operations leaving zero transition nodes, force operations entering transition state, maintenance preserving or creating replicas as expected, automatic expiry returning nodes to service, dead maintenance node restart causing new replicas, and decommission monitor tracking restored maintenance nodes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/node/TestDecommissionAndMaintenance.java -->
