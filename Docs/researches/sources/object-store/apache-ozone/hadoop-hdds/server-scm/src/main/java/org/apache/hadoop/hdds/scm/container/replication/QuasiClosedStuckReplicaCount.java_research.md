# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/QuasiClosedStuckReplicaCount.java

Purpose: `QuasiClosedStuckReplicaCount` counts replicas for quasi-closed stuck Ratis containers by origin datanode. This preserves diverged container histories: origins with the highest healthy BCSID are considered best origins and get more target copies, while other origins still receive configured preservation copies.

Important APIs and behavior: the constructor groups all replicas by `originDatanodeId`, separately tracks in-service and maintenance replicas by origin, flags whether any healthy or out-of-service replicas exist, and computes best origins by the maximum non-unhealthy sequence ID. Public APIs include `availableOrigins`, `hasOutOfServiceReplicas`, `hasHealthyReplicas`, `isUnderReplicated`, `isOverReplicated`, `getUnderReplicatedReplicas`, and `getOverReplicatedOrigins`. `MisReplicatedOrigin` carries a source set and replica delta.

Control flow: for a single origin, normal target is three in-service copies, or `minHealthyForMaintenance` when maintenance replicas exist. For multiple origins, best origins target `bestOriginCopies`, all others target `otherOriginCopies`; when maintenance replicas exist, the under-replication path requires at least one online copy of the origin. Over-replication ignores maintenance replicas and compares in-service count with the same target.

State and persistence: all state is in-memory maps and flags derived at construction time. There is no mutation after construction except through mutable sets held internally, and no persistence.

Dependencies and integration: it depends on `ContainerReplica`, `DatanodeID`, and datanode operational states. It is consumed by quasi-closed stuck under/over handlers and configured by `ReplicationManagerConfiguration` best/other origin copy settings.

Risks: only non-unhealthy replicas with non-null sequence IDs participate in best-origin ranking; origins with all unhealthy replicas are never best. If all replicas are unhealthy, best origin set is empty and multi-origin logic applies other-origin targets. Maintenance handling for multiple origins intentionally requires only one online copy, which is a lower target than normal and should remain aligned with the quasi-closed stuck design.

Test signals: `TestQuasiClosedStuckReplicaCount` is extensive and covers single/multiple origin under/over counts, best BCSID ranking, tied best origins, maintenance behavior, all-unhealthy cases, out-of-service flags, and changing origin copy targets.
