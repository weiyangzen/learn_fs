# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestQuasiClosedStuckOverReplicationHandler.java

Purpose: Tests `QuasiClosedStuckOverReplicationHandler`, which deletes excess replicas for quasi-closed stuck Ratis containers while preserving required copies per origin. The key model is origin-aware: best origin by highest BCSID has a different target copy count from other origins.

Important APIs and types: Uses `QuasiClosedStuckOverReplicationHandler`, `RatisReplicationConfig`, `ContainerInfo`, `ContainerReplica`, `DatanodeID`, `ContainerReplicaOp`, `DeleteContainerCommand` via `SCMCommand`, `ReplicationManagerMetrics`, and throttled delete dispatch.

Control flow: Setup creates a quasi-closed Ratis container, a push-replication config, mocked healthy node status, metrics, and captured throttled delete commands. Tests assert no commands when origin groups are at target, and no action when pending delete ops exist. Over-replicated scenarios create origin1 with higher BCSID and too many copies, plus origin2 at target, expecting one delete. A throttling test creates two over-replicated origins, injects an overloaded delete on the first attempt, confirms the handler continues to process the second origin, and rethrows. A final case ensures no delete when the best origin and other origin are exactly at configured targets.

State and persistence behavior: State is in-memory origin/BCSID distribution and command capture. The handler does not persist metadata; behavior is visible through returned command counts and the command set.

Dependencies and integration points: Depends on `QuasiClosedStuckReplicaCount` semantics, replication-manager config for quasi-closed stuck copy targets, node status, and throttled delete command delivery.

Risks and test signals: Risks include deleting a required origin copy, ignoring pending deletes, failing to continue after one target overload, or not rethrowing to allow retry. Signals are returned counts, command type checks, command-set size, and `CommandTargetOverloadedException` assertions.
