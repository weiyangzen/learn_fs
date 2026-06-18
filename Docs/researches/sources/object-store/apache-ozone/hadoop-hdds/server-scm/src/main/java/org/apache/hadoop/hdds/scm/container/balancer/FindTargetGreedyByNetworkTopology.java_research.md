# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/FindTargetGreedyByNetworkTopology.java

Purpose: target selection strategy that sorts target candidates by network topology distance from the selected source, then by usage.

Important APIs: constructor wiring `ContainerManager`, `PlacementPolicyValidateProxy`, `NodeManager`, and `NetworkTopology`; `sortTargetForSource`; `resetPotentialTargets`.

Control flow and state: stores potential targets in a raw `LinkedList` passed to `AbstractFindTargetGreedy`. Sorting computes `networkTopology.getDistanceCost(source, target)` and uses inherited `compareByUsage` as tie breaker. Reset transforms datanode details into current `DatanodeUsageInfo` snapshots from `NodeManager`.

Dependencies and integration: depends on topology map, target placement validation, and inherited target selection logic. Tested by `TestFindTargetStrategy` for nearest-target ordering.

Risks: raw `List` loses generic compile-time safety; `networkTopology` must be non-null. Distance subtraction can theoretically overflow if distance costs grow, though current costs are small. Test signals should cover equal-distance usage tiebreaks, null topology rejection, and placement-policy filtering through the superclass.
