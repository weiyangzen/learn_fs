<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestQuasiClosedStuckReplicationCheck.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestQuasiClosedStuckReplicationCheck.java

Purpose: This class tests `QuasiClosedStuckReplicationCheck`, the health check for quasi-closed containers that cannot be force-closed normally and need missing, under-replicated, or over-replicated repair handling.

Important APIs and types: It uses `QuasiClosedStuckReplicationCheck`, `ReplicationManager.ReplicationManagerConfiguration`, `ReplicationManagerReport`, `ReplicationQueue`, `ContainerCheckRequest`, `ContainerReplicaOp`, `ContainerHealthState.QUASI_CLOSED_STUCK_*`, and `ReplicationTestUtil` helpers for origin and sequence-ID controlled replicas.

Control flow: Setup creates real Replication Manager configuration from `OzoneConfiguration`, a fresh report, and a queue. Closed containers, non-stuck quasi-closed containers, and quasi-closed containers that still have an open replica are ignored. Missing containers are reported but not queued. Under-replicated stuck containers are queued unless a pending add already addresses them. Over-replicated stuck containers are queued unless a pending delete already addresses them.

State and persistence behavior: The state is in-memory replica origin grouping, sequence IDs, pending add/delete operations, report counters, and queue contents. No DB or filesystem persistence is involved.

Dependencies and integration points: This test integrates with the replication queue contract used by Replication Manager's later command-generation stage and with the combined health-state reporting model for quasi-closed stuck containers.

Risks: The handler distinguishes "not handled" from "handled but not queued" based on pending operations and missing-replica state. Those paths can easily regress if generic Ratis replication logic changes.

Test signals: Strong signals are queue sizes, report counters for `QUASI_CLOSED_STUCK_UNDER_REPLICATED`, `QUASI_CLOSED_STUCK_OVER_REPLICATED`, and `QUASI_CLOSED_STUCK_MISSING`, and boolean return values showing whether the handler consumed the request.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestQuasiClosedStuckReplicationCheck.java -->
