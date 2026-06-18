<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestRatisReplicationCheckHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestRatisReplicationCheckHandler.java

Purpose: This is the main unit suite for `RatisReplicationCheckHandler`, covering Ratis container health classification and enqueue behavior for under-replication, over-replication, mis-replication, maintenance/decommission scenarios, unhealthy replicas, mismatched replica states, and quasi-closed sequence-ID edge cases.

Important APIs and types: It exercises `RatisReplicationCheckHandler.checkHealth` and `handle`, `ContainerHealthResult` subtypes (`UnderReplicatedHealthResult`, `OverReplicatedHealthResult`, `MisReplicatedHealthResult`), `ReplicationQueue`, `ReplicationManagerReport`, `PlacementPolicy.validateContainerPlacement`, `ContainerPlacementStatusDefault`, `NodeStatus`, `ContainerReplicaOp`, and `ReplicationTestUtil` replica builders.

Control flow: Setup mocks placement as initially satisfied and node status as in-service healthy. Tests first reject non-Ratis containers, then inspect direct health results before checking `handle` side effects. Under-replicated paths vary live replica count, pending deletes, pending adds, out-of-service nodes, all-out-of-service parameterized node states, unrecoverable no-replica cases, and unhealthy replicas. Over-replicated paths vary extra healthy replicas, unhealthy excess, mismatched replicas, pending deletes, maintenance replicas, and safe-over-replication gating. Mis-replication is injected by mocking placement failure and verifying whether it queues as under-replication. Quasi-closed tests validate sequence ID compatibility and unique origin behavior.

State and persistence behavior: There is no durable state. Runtime state includes replica state, datanode operational state, sequence ID, origin datanode ID, pending operations, placement result, request maintenance redundancy, report counters, and queue entries.

Dependencies and integration points: This suite is the compatibility anchor between the Ratis replica-counting policy, placement policy, Replication Manager node status lookup, report counters, and work queues consumed by replication/deletion processors.

Risks: The class encodes many overlapping conditions where a container can be under-replicated, over-replicated, mis-replicated, or temporarily fixed by pending operations. It also protects special behavior for all-unhealthy replicas and quasi-closed origins that generic counting could mishandle.

Test signals: Signals include exact health-state subtype, remaining or excess redundancy, `isReplicatedOkAfterPending`, `underReplicatedDueToOutOfService`, `isUnrecoverable`, mismatched/safe-over-replication flags, queue sizes, and report counters for `UNDER_REPLICATED`, `OVER_REPLICATED`, `MIS_REPLICATED`, and `MISSING`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestRatisReplicationCheckHandler.java -->
