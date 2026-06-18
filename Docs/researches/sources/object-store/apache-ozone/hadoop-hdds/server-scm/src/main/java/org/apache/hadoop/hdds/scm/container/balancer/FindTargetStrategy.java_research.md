# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/FindTargetStrategy.java

Purpose: target strategy interface for choosing where a specific container from a source should move and for tracking incoming bytes.

Important APIs: `findTargetForContainerMove`, `increaseSizeEntering`, `reInitialize`, `resetPotentialTargets`, `getSizeEnteringNodes`, and `clearSizeEnteringNodes`.

Control flow and state: implementations own candidate ordering, placement validation, and size-limit enforcement. The interface exposes incoming-size state for iteration status reporting.

Dependencies and integration: used by Container Balancer task with `ContainerID`, `DatanodeDetails`, `DatanodeUsageInfo`, and `ContainerBalancerConfiguration`; implemented by network-topology and usage-info greedy variants.

Risks: Javadoc mentions a functional interface that is not present in the method signature, likely stale from an older API. Tests should validate both implementations under the same interface contract: no target, failed placement, size entering max, and reset semantics.
