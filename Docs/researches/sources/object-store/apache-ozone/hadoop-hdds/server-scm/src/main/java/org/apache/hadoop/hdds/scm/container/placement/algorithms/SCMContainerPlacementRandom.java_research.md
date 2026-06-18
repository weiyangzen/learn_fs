# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/SCMContainerPlacementRandom.java

Purpose: simple random placement policy that chooses healthy datanodes without utilization or topology weighting.

Important APIs: constructor, `chooseDatanodesInternal`, and `chooseNode`.

Control flow and state: base class filters available healthy nodes by used/excluded/favored and space requirements. If more nodes are needed, `getResultSet` repeatedly calls `chooseNode`, which selects a random element, removes it, and increments metrics.

Dependencies and integration: implements `PlacementPolicy`, extends `SCMCommonPlacementPolicy`, uses `NodeManager`, config, and metrics. Tested by `TestSCMContainerPlacementRandom` and some pipeline manager tests.

Risks: metrics must be non-null. Random behavior makes statistical assertions fragile; tests should seed or mock randomness where possible. Since the policy intentionally ignores balancing, deployments relying on it need balancer coverage.
