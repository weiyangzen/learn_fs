# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestRatisMisReplicationHandler.java

Purpose: Tests `RatisMisReplicationHandler`, the Ratis specialization of the shared mis-replication repair flow. It verifies placement repair by copying from eligible replicas without EC replica indexes.

Important APIs and types: Uses `RatisMisReplicationHandler`, shared `TestMisReplicationHandler`, `RatisReplicationConfig`, `PlacementPolicy`, `ContainerPlacementStatus`, `ContainerReplicaOp`, `SCMException`, `CommandTargetOverloadedException`, and Ratis replica states including `QUASI_CLOSED`.

Control flow: Setup configures a closed Ratis container with factor three through the abstract harness. Parameterized tests vary mis-replication count for all in-service closed replicas and quasi-closed replicas, expecting at most three targets. Other tests cover placement no-node exceptions, maintenance replicas excluded from sources, no repair when under- or over-replicated, no repair when placement is already satisfied, no repair with pending add/delete, and overload propagation when all sources are throttled.

State and persistence behavior: State is the base harness in-memory container, replica set, pending ops, placement mocks, command capture, and metrics. The Ratis-specific assertion requires every `ReplicateContainerCommand` to have replica index zero.

Dependencies and integration points: Integrates with placement policy, replication-manager throttled replication command path, node op-state filtering, and common mis-replication command assertions inherited from the base class.

Risks and test signals: Risks are issuing Ratis commands with EC-style indexes, copying maintenance replicas, repairing containers that are not purely mis-replicated, and swallowing throttling. Signals are command counts, exception assertions, source/target membership, and replica-index-zero checks.
