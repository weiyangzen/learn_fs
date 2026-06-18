<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerBalancerSelectionCriteria.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerBalancerSelectionCriteria.java

## Purpose
Determines which containers on a candidate source datanode are eligible for balancing. It filters by include/exclude lists, prior selection, per-source leaving limits, per-iteration move-size limit, lifecycle/replica state, replication health, and in-flight replication/deletion.

## Important APIs, Types, And Functions
`getContainerIDSet` returns a cached, used-bytes-descending candidate set per datanode. `shouldBeExcluded` applies the main eligibility checks. `isContainerClosed` and `isContainerHealthyForMove` implement strict mode. `isContainerClosedRelaxed`, `hasMinClosedReplicas`, and `isContainerHealthyForMoveRelaxed` support `includeNonStandardContainers`. `addToExcludeDueToFailContainers` prevents repeated failures on a container. `getCandidateContainers` reads `NodeManager` membership and pre-filters configured include/exclude sets and already selected containers.

## Control Flow
For a source, candidates are fetched once and cached in a `TreeSet` ordered by largest used bytes first. Each balancing attempt calls `shouldBeExcluded`; excluded IDs are removed from the cached set by the task. Strict mode requires CLOSED container and CLOSED source replica plus HEALTHY replication state. Relaxed mode permits selected CLOSED/QUASI_CLOSED and OVER_REPLICATED cases with minimum closed replica and non-empty source-replica checks.

## State And Persistence
State is per-iteration memory: cached candidate sets, failed-container excludes, configured include/exclude sets, and selected container-to-source map references. It does not persist state.

## Dependencies And Integration Points
Depends on `NodeManager`, `ContainerManager`, `ReplicationManager`, `FindSourceStrategy`, container health results, protobuf lifecycle/replica states, and balancer configuration. It feeds `ContainerBalancerTask.matchSourceWithTarget`.

## Risks And Test Signals
`getCandidateContainers` mutates the set returned by `nodeManager.getContainers`; if that is not a defensive copy, configured filtering could affect node-manager state. The comparator returns 0 on missing container lookup, which can collapse distinct IDs in a `TreeSet`. Relaxed non-standard eligibility is subtle and must preserve replication safety. Tests should cover include-only mode, exclude lists, failed-container exclusion, selected-container exclusion, source leaving limit, per-iteration size limit, strict closed/healthy checks, relaxed over-replicated/quasi-closed cases, and NodeNotFound handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerBalancerSelectionCriteria.java -->
