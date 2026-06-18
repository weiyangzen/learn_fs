<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestECMisReplicationCheckHandler.java -->
## sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestECMisReplicationCheckHandler.java

Purpose: tests EC placement-policy mis-replication detection and queueing behavior.

Important APIs and types: `ECMisReplicationCheckHandler`, `PlacementPolicy.validateContainerPlacement`, `ContainerPlacementStatusDefault`, `ContainerHealthResult`, `ReplicationQueue`, `ContainerReplicaOp`, and `ContainerHealthState.MIS_REPLICATED`.

Control flow: setup mocks placement as satisfied by default and builds a request with queue, report, pending ops, and maintenance redundancy. Tests assert healthy EC containers and non-EC containers return false. Mis-replicated EC containers are queued to the under-replicated queue and counted as `MIS_REPLICATED`. Pending ADD can make placement OK after pending and suppress queueing. A pending DELETE for an excess unhealthy replica can also suppress queueing.

State and persistence behavior: queue and report counters are the mutable state. Pending ADD/DELETE records alter whether the current violation needs active processing.

Dependencies and integration points: depends on EC replication configs, placement-policy validation, pending operations, and the replication queue used by the manager.

Risks: placement status must be evaluated with the correct datanode set after pending operations. Mis-replication is queued on the under-replicated path, so prioritization and processor behavior matter.

Test signals: health-state result, handler return, queue sizes, and exact report counters for under/over/mis replication.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/health/TestECMisReplicationCheckHandler.java -->
