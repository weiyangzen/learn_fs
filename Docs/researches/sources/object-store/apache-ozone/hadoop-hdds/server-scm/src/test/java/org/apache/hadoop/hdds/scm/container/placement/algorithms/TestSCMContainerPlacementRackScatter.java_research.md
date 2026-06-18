# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/TestSCMContainerPlacementRackScatter.java

Purpose: This suite verifies the EC/pipeline rack-scatter placement policy, which tries to maximize rack diversity for selected nodes and existing replicas. It covers cluster shapes from small single-rack cases to 30 datanodes, failure modes, fallback behavior, validation, and repair-adjacent selection scenarios.

Important APIs and types: It uses `SCMContainerPlacementRackScatter`, `SCMContainerPlacementMetrics`, `NetworkTopologyImpl`, `NodeSchemaManager`, `NodeManager`, `DatanodeInfo`, `NodeStatus`, `ContainerPlacementStatus`, `SCMException` result codes, and `OZONE_SCM_PIPELINE_PLACEMENT_IMPL_KEY`.

Control flow: Setup builds configurable topologies with a fixed number of nodes per rack or one node per rack plus extras, mocks node manager lookups, and initializes a rack-scatter policy. Tests choose nodes with no exclusions, with used/excluded/favored nodes, with insufficient racks, with default rack locations, and with storage reports adjusted to remove candidates. Helper assertions combine used and chosen nodes and validate the resulting rack spread.

State and persistence behavior: There is no persistence. State is in topology membership, datanode status, storage reports, metric counters, used/excluded/favored lists, and pending selected-node lists. Tests mutate storage space and remove nodes from the topology to model unavailable nodes.

Dependencies and integration points: Rack scatter is central to EC placement and can also be configured for pipeline placement. It integrates rack-count calculation, available-node filtering, fallback semantics, and placement validation used by replication health.

Risks: Randomized selection means many assertions validate rack count and membership constraints rather than exact order. Some tests target known edge cases, such as choosing one node when two racks are ideally required, all nodes on a rack excluded, and insufficient available nodes; these are sensitive to algorithm changes.

Test signals: Exact selected counts, rack-size equality with `min(required, rack count)`, specific `SCMException` result codes, favored/excluded behavior, default-rack collapse to one rack, validation misreplication counts, and chosen nodes from expected racks under edge-case constraints.
