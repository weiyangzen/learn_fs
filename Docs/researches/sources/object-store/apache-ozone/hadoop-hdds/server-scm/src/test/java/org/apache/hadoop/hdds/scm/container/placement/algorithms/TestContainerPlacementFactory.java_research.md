# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/TestContainerPlacementFactory.java

Purpose: This test validates `ContainerPlacementPolicyFactory` policy construction and a basic rack-aware placement result. It ensures configured classes instantiate correctly, EC placement defaults to rack scatter, and invalid or incompatible policy classes fail.

Important APIs and types: It uses `ContainerPlacementPolicyFactory.getPolicy`, `getECPolicy`, `SCMContainerPlacementRackAware`, `SCMContainerPlacementRackScatter`, `PlacementPolicy`, `ContainerPlacementStatusDefault`, `SCMContainerPlacementMetrics`, `NodeManager`, `DatanodeInfo`, `NetworkTopologyImpl`, `NodeSchemaManager`, storage and metadata reports, and SCM config keys.

Control flow: The rack-aware test configures the placement implementation class, initializes a three-rack topology with 15 datanodes, injects storage reports with varied free space, mocks `NodeManager` lookups, obtains a policy from the factory, and asks for three datanodes. Other tests assert class identity for configured rack-aware and EC policies. Negative tests configure a dummy `PlacementPolicy` lacking the expected constructor or a nonexistent class and assert exceptions.

State and persistence behavior: There is no persistence. State is configuration, topology membership, datanode info storage reports, and metrics object creation.

Dependencies and integration points: The factory is the integration point between SCM configuration and placement algorithm implementations. The test also covers network topology and node manager metadata required by rack-aware placement.

Risks: Reflection-based constructor checks are brittle by design. The topology test relies on random choice satisfying rack placement rules and on singleton `NodeSchemaManager` initialization. It does not exhaustively test every policy constructor path.

Test signals: Signals include policy class identity, three selected datanodes, first two selected on the same rack and third on another rack, and expected exceptions for invalid implementation configuration.
