<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/AbstractFindTargetGreedy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/AbstractFindTargetGreedy.java

## Purpose
Provides common greedy target-selection logic for container balancer strategies. It chooses an eligible target datanode for a candidate source/container while honoring placement policy, duplicate-replica avoidance, target ingress limits, and post-move utilization limits.

## Important APIs, Types, And Functions
Implements `FindTargetStrategy`. `findTargetForContainerMove` sorts targets through subclass `sortTargetForSource`, then tests each target. `containerMoveSatisfiesPlacementPolicy` validates the replica set after replacing the source with the target. `canSizeEnterTarget` enforces `maxSizeEnteringTarget` and upper utilization limit. `increaseSizeEntering` updates per-target scheduled ingress and reorders/removes targets. `reInitialize`, `resetTargets`, `getSizeEnteringNodes`, and `clearSizeEnteringNodes` manage per-iteration state.

## Control Flow
At iteration start, potential targets are loaded and each target's scheduled ingress starts at zero. For a candidate move, targets are sorted by the concrete strategy, existing replicas are rejected, placement is revalidated, and projected ingress/utilization is checked. After a move is scheduled, the target's scheduled ingress increases and the target is reinserted only if it remains below the ingress cap.

## State And Persistence
State is per-task, per-iteration memory: `sizeEnteringNode`, potential targets, configuration, upper limit, and dependencies. No persistence is performed.

## Dependencies And Integration Points
Depends on `ContainerManager`, `PlacementPolicyValidateProxy`, `NodeManager`, `DatanodeUsageInfo`, `ContainerReplica`, `ContainerInfo`, and `ContainerBalancerConfiguration`. Concrete subclasses provide usage-only or network-topology-aware sorting.

## Risks And Test Signals
`potentialTargets` is a collection supplied by subclasses and is mutated during balancing, so ordering and remove/add semantics matter. Missing `sizeEnteringNode` records cause warnings and reject moves. Tests should cover duplicate target replica rejection, placement-policy rejection, ingress cap, upper-limit projection, target reordering after ingress, missing container handling, and subclass sorting effects.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/AbstractFindTargetGreedy.java -->
