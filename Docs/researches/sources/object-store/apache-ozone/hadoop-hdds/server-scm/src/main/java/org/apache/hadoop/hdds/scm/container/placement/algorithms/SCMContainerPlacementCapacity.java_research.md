# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/SCMContainerPlacementCapacity.java

Purpose: capacity-biased placement policy using the "power of two choices": randomly sample two healthy candidates and choose the lower-utilization node.

Important APIs: constructor, `chooseDatanodesInternal`, and `chooseNode`.

Control flow and state: delegates base filtering to `SCMCommonPlacementPolicy`, increments placement metrics, returns preselected healthy nodes if enough are already chosen, otherwise repeatedly chooses from the healthy list. `chooseNode` removes the selected node from the candidate list.

Dependencies and integration: uses `NodeManager.getNodeStat` and `SCMNodeMetric.isGreater` to compare utilization. Tests exist in `TestSCMContainerPlacementCapacity` and older placement tests.

Risks: metrics must be non-null; node stats must be available for sampled nodes. If both random indexes match, only one node is considered. Test signals should cover removal, metric increments, low-utilization bias, insufficient healthy nodes through the superclass, and zero-capacity stats handled by `SCMNodeMetric`.
