# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestQuasiClosedStuckUnderReplicationHandler.java

Purpose: Tests `QuasiClosedStuckUnderReplicationHandler`, which copies under-replicated quasi-closed stuck origin groups until best and other origins meet configured copy targets.

Important APIs and types: Uses `QuasiClosedStuckUnderReplicationHandler`, `RatisReplicationConfig`, `PlacementPolicy`, `ContainerHealthResult.UnderReplicatedHealthResult`, `ContainerReplica`, `ContainerReplicaOp`, `DatanodeID`, `ReplicationManagerConfiguration`, `InsufficientDatanodesException`, and `SCMException`.

Control flow: Setup creates a quasi-closed Ratis container, simple placement policy, push-replication config, metrics, pending-op mock, healthy node status, and command captures for throttled replication/delete. Tests assert no action when not under-replicated and no action when pending add ops exist. A one-copy origin schedules two copies to reach the best-origin target. Overload handling creates two deficient origins, injects an overloaded source, verifies another command can still be sent, and expects the overload exception to be rethrown. No-node and insufficient-node policies produce `SCMException` and `InsufficientDatanodesException` respectively, with partial command counts. The origin-copies test overrides config to best=3 and other=2 and verifies only the deficient best origin is copied.

State and persistence behavior: State is in-memory: origin/BCSID replica sets, pending ops, configurable copy targets, and captured commands. There is no durable write; command count is the behavioral side effect.

Dependencies and integration points: Depends on placement policy target choice, replication-manager push replication dispatch, metrics/config, pending-op accounting, and `QuasiClosedStuckReplicaCount` output.

Risks and test signals: Risks include scheduling duplicate work while pending ops exist, losing partial progress on insufficient nodes, swallowing overloaded exceptions, and ignoring configured copy targets. Signals are command counts, exception types, and config-specific expected counts.
