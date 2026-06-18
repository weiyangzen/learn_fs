# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/FindSourceStrategy.java

Purpose: strategy interface for choosing source datanodes and tracking outgoing data during a balancing iteration.

Important APIs: candidate polling/removal/re-addition, `increaseSizeLeaving`, `canSizeLeaveSource`, `reInitialize`, `resetPotentialSources`, and outgoing-size map access/clear.

Control flow and state: the interface defines mutable iteration state but leaves storage and ordering to implementations. The comments warn that `addBackSourceDataNode` does not check duplicates and callers own removal when needed.

Dependencies and integration: integrates `DatanodeDetails`, `DatanodeUsageInfo`, and `ContainerBalancerConfiguration`; implemented by `FindSourceGreedy` and called from Container Balancer selection loops.

Risks: Javadoc for `canSizeLeaveSource` still says target in places, which can mislead maintainers. Implementations should be tested through both direct strategy tests and balancer task tests for size accounting and queue exhaustion.
