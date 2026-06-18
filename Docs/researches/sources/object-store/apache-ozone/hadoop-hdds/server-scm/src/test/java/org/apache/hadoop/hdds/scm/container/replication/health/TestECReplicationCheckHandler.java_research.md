<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestECReplicationCheckHandler.java -->
## sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestECReplicationCheckHandler.java

Purpose: exhaustively tests EC health classification for under-replication, over-replication, unrecoverable/missing/unhealthy states, out-of-service replicas, pending operations, and precedence among under/over/mis conditions.

Important APIs and types: `ECReplicationCheckHandler`, `ContainerHealthResult.UnderReplicatedHealthResult`, `OverReplicatedHealthResult`, `ReplicationQueue`, `ContainerReplicaOp` ADD/DELETE, `ContainerHealthState`, `ECReplicationConfig`, `NodeOperationalState`, and `ContainerReplicaProto.State.UNHEALTHY`.

Control flow: setup uses EC 3-2, queue, report, and maintenance redundancy. Tests call `checkHealth` for direct result details and `handle` for queue/report effects. Cases include healthy full sets, missing indexes, pending adds, decommission/maintenance-driven under-replication, unrecoverable data loss, unhealthy replicas, offline indexes with and without pending repair, excess replicas, pending deletes, maintenance over-replication ignored as healthy, and combinations where under-replication takes precedence over over/mis-replication while over-replication takes precedence over mis-replication.

State and persistence behavior: no persistence. State under test is report counters and queue contents. Pending operations can suppress queue insertion while still leaving report counters incremented because the current physical state is not yet repaired.

Dependencies and integration points: integrates EC replica-index math, maintenance redundancy policy, out-of-service node semantics, pending operations, and report/queue contracts consumed by `ReplicationManager`.

Risks: EC safety hinges on distinguishing recoverable missing indexes from unrecoverable data loss and on not treating maintenance extras as harmful over-replication. Combined states such as `MISSING_UNDER_REPLICATED` and `UNHEALTHY_UNDER_REPLICATED` are sensitive to classification order.

Test signals: direct assertions on remaining redundancy, `isReplicatedOkAfterPending`, `underReplicatedDueToOutOfService`, `isUnrecoverable`, offline-index flags, queue sizes, and all relevant health counters.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestECReplicationCheckHandler.java -->
