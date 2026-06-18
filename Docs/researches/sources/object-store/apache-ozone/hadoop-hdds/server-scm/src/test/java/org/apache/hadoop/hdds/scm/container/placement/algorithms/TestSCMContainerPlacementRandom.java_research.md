# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/TestSCMContainerPlacementRandom.java

Purpose: This test covers the baseline random placement policy: choosing valid nodes while excluding existing nodes, validating the minimal placement policy, and rejecting datanodes without enough data or metadata space.

Important APIs and types: It uses `SCMContainerPlacementRandom`, `SCMContainerPlacementMetrics`, `ContainerPlacementStatus`, `NodeManager`, `DatanodeInfo`, `NodeStatus`, storage and metadata reports, `OzoneConfiguration`, and the minimum RATIS volume free-space config.

Control flow: `chooseDatanodes` builds five healthy datanodes, marks one low on data space, excludes two existing nodes, and repeatedly asserts the chosen target is neither excluded nor low-space. `testPlacementPolicySatisified` verifies the random policy's relaxed one-rack placement semantics. `testIsValidNode` creates three datanodes and independently makes one data-space constrained and one metadata-space constrained, then calls `isValidNode`.

State and persistence behavior: There is no persistence. State is stored in mocked node manager responses, `DatanodeInfo` storage reports, exclusion lists, and policy validation results.

Dependencies and integration points: Random placement is the base/simple SCM placement behavior and shares free-space validation with other placement policies. Its validation result is consumed by replication and placement health logic.

Risks: The spelling of `testPlacementPolicySatisified` is cosmetic. The random chooser loop is probabilistic but only checks exclusion constraints, so it is robust against exact random order. The test uses small byte-sized thresholds.

Test signals: Chosen node count is one, excluded and low-space datanodes are never selected, empty placement is unsatisfied with one missing placement, single-node placement is satisfied for the random policy, and `isValidNode` distinguishes data-space and metadata-space shortages.
