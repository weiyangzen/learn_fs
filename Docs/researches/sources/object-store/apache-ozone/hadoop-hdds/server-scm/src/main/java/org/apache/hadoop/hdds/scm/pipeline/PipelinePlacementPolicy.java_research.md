# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelinePlacementPolicy.java

## Purpose
`PipelinePlacementPolicy` chooses datanodes for Ratis pipeline creation using health, space, pipeline-load limits, and rack/topology awareness.

## Important APIs, Types, And Functions
It extends `SCMCommonPlacementPolicy`. `currentRatisThreePipelineCount` counts non-closed Ratis factor-three pipelines on a datanode. `filterPipelineLimit` sorts viable datanodes by current pipeline count and filters by `nodeManager.pipelineLimit`. `filterViableNodes` applies healthy-state, space, excluded/used-node, load-limit, and multi-rack checks. `chooseDatanodesInternal` chooses randomly when topology is absent/single-rack or calls `getResultSetWithTopology`. Topology helpers include `getAnchorAndNextNode`, `chooseNode`, `chooseFirstNode`, `chooseNodeBasedOnRackAwareness`, `chooseNodeBasedOnSameRack`, and `fallBackPickNodes`.

## Control Flow
Selection starts from `NodeStatus.inServiceHealthy()` nodes. It filters nodes with enough metadata/data space, removes excluded and already-used nodes, and checks count sufficiency. It then filters by pipeline limit and detects the case where a multi-rack cluster has only one rack remaining after load filtering, failing with a specific message.

For topology-aware factor-three placement, it chooses an anchor node, tries to choose a second node on a different rack, then chooses remaining nodes preferably on the anchor rack. If same-rack topology choice fails, it falls back to random available nodes. Used-node handling supports zero, one, or two preselected nodes and rejects larger used-node sets. Required rack count is fixed at two, while max replicas per rack allows all replicas on one rack only when there is only one rack.

## State And Persistence Behavior
The policy is stateless aside from collaborator references and configured datanode pipeline limit. It reads live node and pipeline state but does not persist anything. It mutates local candidate lists during selection.

## Dependencies And Integration Points
It depends on `NodeManager`, `PipelineStateManager`, `NetworkTopology`, `RatisReplicationConfig`, `SortedList`, `SCMCommonPlacementPolicy`, and SCM config keys. It is created by `PipelinePlacementPolicyFactory` and used by `RatisPipelineProvider`.

## Risks And Edge Cases
Placement depends on current node-to-pipeline reverse indexes; stale indexes can over- or under-count pipeline load. The `checkAllNodesAreEqual` helper treats `topology.getNumOfNodes(maxLevel - 1) == 1` as all nodes equal, so topology assumptions must match `NetworkTopology` semantics. `removePeers(nextNode, healthyNodes)` is called even when `nextNode` may be null in one branch; this relies on superclass behavior tolerating null or branch conditions avoiding harm. Load failure messages use configured `datanodePipelineLimit`, but effective limits may come from `nodeManager.pipelineLimit`.

## Test Signals
Tests should cover healthy/space filtering, excluded and used nodes, pipeline-limit sorting, multi-rack failure after filtering, factor-three rack distribution, fallback selection, used-node sizes zero/one/two/too-many, single-rack behavior, current pipeline count ignoring closed/non-Ratis/non-factor-three pipelines, and interaction with dynamic per-node pipeline limits.
