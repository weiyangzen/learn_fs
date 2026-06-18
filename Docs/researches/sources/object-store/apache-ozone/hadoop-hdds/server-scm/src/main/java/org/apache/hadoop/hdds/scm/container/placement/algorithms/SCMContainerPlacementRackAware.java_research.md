# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/SCMContainerPlacementRackAware.java

Purpose: rack-aware placement policy for replicated containers, following HDFS-style 3-replica layout with two replicas on one rack and the third on another when racks allow.

Important APIs: `chooseDatanodesInternal`, legacy choose path, private `chooseNode` and `chooseNodes`, plus rack-policy overrides `getMaxReplicasPerRack` and `getRequiredRackCount`.

Control flow and state: validates node counts, filters favored nodes, handles new-pipeline versus add-replica scenarios, and chooses nodes with same-rack affinity or cross-rack exclusion. `chooseNode` retries random topology selection, checks disk resources via superclass `isValidNode`, and optionally falls back by dropping affinity or rack constraints.

Dependencies and integration: depends on `NetworkTopology`, `NodeManager`, `SCMCommonPlacementPolicy`, and `SCMContainerPlacementMetrics`. Covered by `TestSCMContainerPlacementRackAware` and factory tests.

Risks: in the branch for two or more used nodes with all used nodes on different racks, code references `chosenNodes.get(0)` before any node is added, which looks like an `IndexOutOfBoundsException` path. Favored nodes are accepted in some branches without a local `isValidNode` check. Tests should cover that all-used-on-different-racks add-replica case, fallback disabled behavior, excluded/favored overlap, and capacity failure retry accounting.
