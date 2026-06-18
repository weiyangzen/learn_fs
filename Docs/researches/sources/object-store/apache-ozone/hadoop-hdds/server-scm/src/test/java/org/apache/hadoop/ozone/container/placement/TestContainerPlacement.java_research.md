# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/ozone/container/placement/TestContainerPlacement.java

Purpose: This simulation test compares SCM's capacity-aware container placement with random placement and asserts that capacity-aware placement improves cluster space distribution over many create/delete operations.

Important APIs and types: It uses `MockNodeManager`, `NodeManager`, `NodeStatus.inServiceHealthy`, `SCMContainerPlacementCapacity`, `SCMContainerPlacementRandom`, `SCMContainerPlacementMetrics`, `SCMNodeStat`, `DatanodeDetails`, `OzoneConfiguration`, `DescriptiveStatistics`, and `OzoneConsts.GB`.

Control flow: The test creates two comparable 100-node mock clusters, computes initial standard deviation of used/capacity ratios, instantiates capacity and random placement policies, then runs 200,000 simulated operations. For each operation it chooses three datanodes, randomly picks container and metadata sizes, and either adds or deletes container usage every fifth iteration. It compares final standard deviations.

State and persistence behavior: There is no durable state. Runtime state is node space accounting inside `MockNodeManager`, which is mutated through `addContainer` and `delContainer`. The test's key state metric is standard deviation of SCM-used fraction across healthy in-service nodes.

Dependencies and integration points: It exercises the placement algorithms against `NodeManager` stats and SCM placement metrics mocks. It is a probabilistic integration point for algorithm behavior rather than a deterministic single-choice unit test.

Risks: The test depends on random operation ordering and a large operation count to stabilize statistics. It asserts a bold statistical claim, so algorithm changes, mock cluster initialization changes, or random distribution shifts can affect stability.

Test signals: Initial cluster standard deviations must match within tolerance; capacity placement must reduce standard deviation versus its starting state; random placement's final standard deviation must remain worse than capacity placement.
