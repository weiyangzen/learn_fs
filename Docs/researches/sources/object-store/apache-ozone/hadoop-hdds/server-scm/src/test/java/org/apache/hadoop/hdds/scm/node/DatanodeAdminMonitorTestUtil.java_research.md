# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/DatanodeAdminMonitorTestUtil.java

Purpose: shared utility class for tests around `DatanodeAdminMonitor` and `NodeDecommissionMetrics`, especially decommission and maintenance progress where replication state must be simulated.

Important APIs and types: `generateReplica()` creates `ContainerReplica` instances and mutates the supplied datanode persisted operational state. `generateReplicaCount()` builds `RatisContainerReplicaCount`; `generateECReplicaCount()` builds `ECContainerReplicaCount` from tuples of node state, datanode, and replica index. `mockGetContainerReplicaCount()` and `mockGetContainerReplicaCountForEC()` reset and configure a mocked `ReplicationManager` to return generated counts. `mockCheckContainerState()` controls whether `ReplicationManagerReport` is incremented as under-replicated. `DatanodeAdminHandler` counts event invocations.

Control flow: mock helpers reset the replication manager, install a default sample-limit config, answer `getContainerReplicaCount` based on the requested container ID, and stub `checkContainerStatus` to either mark under-replication and return true or return false.

State and persistence: no persistent storage. It mutates mock state and datanode operational state in-memory. Dependencies include Mockito, SCM container replication classes, EC/Ratis replication count types, event handling, and protobuf node states.

Integration points and risks: used by admin monitor and metrics tests to isolate workflow behavior from full replication manager complexity. Risks include mock reset erasing prior stubs, helper-generated replica indexes/default sequence IDs not matching every production case, and direct datanode state mutation influencing assertions.
