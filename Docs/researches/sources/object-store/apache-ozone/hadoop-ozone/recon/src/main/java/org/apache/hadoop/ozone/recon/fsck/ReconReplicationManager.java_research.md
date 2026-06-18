## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/fsck/ReconReplicationManager.java

Purpose: Recon-specific extension of SCM `ReplicationManager` that runs read-only health checks over all containers and persists unhealthy states into Recon SQL tables.

Important APIs/types/functions: `InitContext` builder carries parent constructor dependencies; constructor injects `NoOpsContainerReplicaPendingOps`; `start()` is a no-op; `processAll()` performs the scan; `storeHealthStatesToDatabase` maps container health to rows; helpers create `UnhealthyContainerRecord`s for missing, under/over/mis-replicated, negative size, and replica mismatch states.

Control flow: `processAll` builds `ReconReplicationManagerReport`, gets all containers, calls inherited `processContainer(..., readOnly=true)` with a `MonitoringReplicationQueue`, checks data checksum mismatch, then stores results in chunks of 50,000 containers. Persistence loads existing `inStateSince`, deletes old health rows for touched containers, inserts new rows atomically, and logs unmapped SCM states.

State and persistence: writes `UNHEALTHY_CONTAINERS` through `ContainerHealthSchemaManager`; relies on mutable `ContainerInfo.healthState` set by inherited SCM processing. It integrates with container manager, placement policies, SCM context, node manager, health schema, and `ContainerHealthTask`.

Risks: inherited SCM behavior is a moving dependency; unmapped health states are skipped with warnings; `applyExistingInStateSince` is called after an earlier existing lookup causing duplicate reads; actual replica count uses all replicas, not only healthy/available replicas. Tests should cover each health-state mapping, `REPLICA_MISMATCH`, negative size deduplication, empty missing, chunked persistence, preservation of `inStateSince`, no command enqueueing, and unmapped state logging.
