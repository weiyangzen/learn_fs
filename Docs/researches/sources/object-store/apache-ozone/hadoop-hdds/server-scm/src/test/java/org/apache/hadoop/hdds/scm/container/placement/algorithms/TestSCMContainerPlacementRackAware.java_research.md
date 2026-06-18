# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/TestSCMContainerPlacementRackAware.java

Purpose: This large suite verifies RATIS-style rack-aware placement, where two replicas may share a rack and additional replicas should spread across racks when possible. It covers fresh placement, used/excluded/favored nodes, fallback behavior, validation, out-of-service handling, and metrics.

Important APIs and types: It exercises `SCMContainerPlacementRackAware`, `SCMContainerPlacementMetrics`, `NetworkTopologyImpl`, `NodeSchemaManager`, `NodeManager`, `DatanodeInfo`, `NodeStatus`, storage and metadata reports, `ContainerPlacementStatus`, and SCM placement configuration.

Control flow: Setup parameterizes clusters from 3 to 15 datanodes, with five nodes per rack, healthy node statuses, topology membership, and varied low-space nodes. Tests request different replica counts and assert rack relationships. Other tests supply existing/used nodes, excluded nodes, favored nodes, single-node racks, default rack locations, and full-rack exclusion cases. Fallback tests compare policies that allow or prohibit fallback and assert metric counters.

State and persistence behavior: No data is persisted. State lives in topology, datanode info reports, node statuses, selected nodes, and metrics counters. Some tests mutate persisted operational state or `DatanodeInfo` status to simulate decommissioned/read-only nodes.

Dependencies and integration points: This policy feeds SCM container and pipeline placement for replicated containers. It integrates network topology with node health, free-space filtering, and replication manager placement validation.

Risks: Parameterized tests use assumptions for cluster shapes and contain random node selection, so assertions focus on relationships rather than exact identities. Singleton topology schema initialization is shared. Some out-of-service selection tests tolerate SCMException because retry logic may miss the only eligible node.

Test signals: Signals include selected counts, same-rack/different-rack relationships, exclusion and favored-node behavior, SCMException when fallback is prohibited or no valid target exists, metric request/success/attempt/fallback counts, validation misreplication counts, and ignoring out-of-service replicas when evaluating placement.
