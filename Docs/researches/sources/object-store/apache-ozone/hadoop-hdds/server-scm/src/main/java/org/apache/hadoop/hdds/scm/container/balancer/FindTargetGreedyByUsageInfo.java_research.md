# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/FindTargetGreedyByUsageInfo.java

Purpose: greedy target strategy that prioritizes lowest projected datanode usage without considering topology distance.

Important APIs: constructor, no-op `sortTargetForSource`, and `resetPotentialTargets`.

Control flow and state: delegates most behavior to `AbstractFindTargetGreedy`, using a `TreeSet` ordered by inherited `compareByUsage`. Reset reconstructs usage info from `NodeManager` for a fresh iteration view.

Dependencies and integration: relies on `ContainerManager`, `PlacementPolicyValidateProxy`, `NodeManager`, and inherited size-entering accounting. Tests in `TestFindTargetStrategy` validate usage ordering and target selection behavior.

Risks: because `TreeSet` comparator equality collapses entries, two datanodes with comparator-equal usage and no stable identity tiebreak in the comparator may cause one to be dropped depending on `compareByUsage`. Test signals should cover equal utilization, equal raw usage, and size-entering updates that change ordering.
