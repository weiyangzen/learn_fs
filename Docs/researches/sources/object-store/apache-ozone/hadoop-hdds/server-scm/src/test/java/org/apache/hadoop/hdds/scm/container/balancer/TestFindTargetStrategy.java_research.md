# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/balancer/TestFindTargetStrategy.java

Purpose: This test covers the target ordering strategies used by container balancer move planning. It verifies that `FindTargetGreedyByUsageInfo` sorts candidate targets by usage and that `FindTargetGreedyByNetworkTopology` prioritizes network proximity before usage when selecting target order for a source datanode.

Important APIs and types: The suite directly exercises `FindTargetStrategy.resetPotentialTargets`, `FindTargetGreedyByUsageInfo.reInitialize`, `sortTargetForSource`, `getPotentialTargets`, `FindTargetGreedyByNetworkTopology`, `DatanodeUsageInfo`, `SCMNodeStat`, `MockNodeManager`, `NetworkTopologyImpl`, `NodeSchemaManager`, and the root/rack/nodegroup/leaf schemas.

Control flow: Usage tests build three `DatanodeUsageInfo` instances with different used-space values, reinitialize the strategy, sort for an arbitrary source, and assert descending usage order. Reset tests create a `MockNodeManager`, restrict potential targets to one datanode, and verify the strategy maps the datanode back to its usage info. Topology tests construct a source and five targets across nodegroups and racks, assert expected distance costs, then verify nearest targets sort ahead of farther but higher-used nodes.

State and persistence behavior: There is no persistence. State is held in strategy candidate collections, generated datanode details, node stats, and the singleton `NodeSchemaManager` topology schema initialization.

Dependencies and integration points: These strategies feed container balancer target selection and depend on SCM node metrics plus network topology distance semantics. The test anchors behavior used before `MoveManager` issues actual container moves.

Risks: The topology test assumes stable distance costs for the configured schema and mutates the singleton schema manager. Equal-distance ordering depends on usage, so changes in tie-breaking or collection ordering can break assertions.

Test signals: Exact target order after sorting, exact potential target count, successful reset to a single mapped `DatanodeUsageInfo`, and expected topology distance costs of 2, 4, and 6.
