<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestClosedWithUnhealthyReplicasHandler.java -->
## sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestClosedWithUnhealthyReplicasHandler.java

Purpose: verifies `ClosedWithUnhealthyReplicasHandler`, which handles closed EC containers that are otherwise sufficiently replicated but have extra unhealthy replicas.

Important APIs and types: `ClosedWithUnhealthyReplicasHandler`, `ContainerCheckRequest`, `ReplicationManager.sendDeleteCommand`, `ReplicationManagerReport`, `ContainerHealthState.UNHEALTHY_OVER_REPLICATED`, `ECReplicationConfig`, and `RatisReplicationConfig`.

Control flow: setup builds a handler with mocked replication manager and request builder. Negative tests cover non-closed containers, RATIS containers, no unhealthy replicas, and EC under-replication. The positive test builds a closed EC 3-2 container with all five healthy indexes plus unhealthy copies for indexes 2 and 5, runs normal and read-only requests, and verifies delete commands target unhealthy indexes.

State and persistence behavior: report state increments `UNHEALTHY_OVER_REPLICATED`; read-only requests update report state but should not send new delete commands. No persistent storage is touched.

Dependencies and integration points: integrates EC replica-index accounting with replication-manager delete command dispatch.

Risks: this handler must run before generic mis/over replication in cases where unhealthy extras block cleaner repair. Deleting a healthy copy instead of the unhealthy copy would reduce durability.

Test signals: handler boolean result, report counter, read-only behavior, and delete-command verification for target replica indexes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestClosedWithUnhealthyReplicasHandler.java -->
