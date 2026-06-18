# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/FindSourceGreedy.java

Purpose: greedy source selection strategy for container balancing. It prefers datanodes with the highest projected utilization after already scheduled outgoing bytes are subtracted.

Important APIs: `reInitialize`, `resetPotentialSources`, `getNextCandidateSourceDataNode`, `increaseSizeLeaving`, `canSizeLeaveSource`, `removeCandidateSourceDataNode`, `addBackSourceDataNode`, and map access/clear methods.

Control flow and state: maintains `sizeLeavingNode` in a `ConcurrentHashMap` and `potentialSources` in a priority queue ordered by projected utilization and datanode ID. `increaseSizeLeaving()` updates outgoing bytes and re-adds the source to the queue, but does not remove an existing queue entry first; callers must manage duplicates via strategy contract or balancer flow.

Dependencies and integration: depends on `NodeManager.getUsageInfo`, `DatanodeUsageInfo.calculateUtilization`, and `ContainerBalancerConfiguration` max outgoing bytes. Used by the balancer task to select overloaded sources and update iteration data.

Risks: `PriorityQueue` is not thread-safe; duplicate entries can skew source selection; missing map entries cause warnings and false decisions. Tests exist around balancer behavior, but direct tests should cover lower-limit enforcement, zero/negative sizes, max outgoing bytes, and requeue ordering.
