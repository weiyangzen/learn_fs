# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/balancer/TestableCluster.java

Purpose: `TestableCluster` is a package-private balancer test fixture that creates a deterministic-shaped but partly random SCM cluster with datanodes, containers, replicas, capacity statistics, and expected utilization boundaries. It supports tests that need realistic container-to-datanode and container-to-replica maps without a live SCM.

Important APIs and types: The helper exposes `getDatanodeToContainersMap`, `getCidToInfoMap`, `getCidToReplicasMap`, `getNodesInCluster`, `getNodeUtilizationList`, `getAverageUtilization`, `getNodeCount`, and `getUnBalancedNodes`. It constructs `DatanodeUsageInfo`, `SCMNodeStat`, `ContainerInfo`, `ContainerID`, `ContainerReplica`, RATIS and EC `ReplicationConfig` instances, and `MockDatanodeDetails`.

Control flow: The constructor creates equally spaced target utilization values, calls `generateData` to assign increasing numbers of variable-size containers to nodes, calls `createReplicasForContainers` to add remaining replicas according to each container replication config, then computes used space, capacity, remaining space, and cluster average utilization. `getUnBalancedNodes` compares generated utilization values with average +/- threshold and returns over-utilized nodes first, then under-utilized nodes.

State and persistence behavior: There is no persistence. All state is in maps keyed by `ContainerID` and `DatanodeUsageInfo`, an array of cluster nodes, generated replica sets, and calculated average utilization. Random replica placement avoids zero-utilization nodes.

Dependencies and integration points: The fixture integrates balancer tests with SCM container metadata, EC/RATIS required-node counts, replica byte accounting, and node capacity statistics. It is intended to feed mocked `ContainerManager`, `NodeManager`, and balancer logic.

Risks: It uses `ThreadLocalRandom`, so replica placement and resulting datanode container membership are nondeterministic. Capacity is derived from generated used bytes and target utilization, with zero-utilization nodes assigned random capacity. Container IDs are computed from loop indexes and may collide if the generation scheme changes.

Test signals: Consumers can assert expected average utilization, expected unbalanced nodes for a threshold, per-datanode container membership, per-container replication sets, and mixed RATIS/EC replication behavior.
