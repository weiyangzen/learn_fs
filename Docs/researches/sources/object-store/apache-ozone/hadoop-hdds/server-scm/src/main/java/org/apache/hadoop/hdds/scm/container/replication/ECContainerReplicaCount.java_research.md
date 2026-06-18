# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/ECContainerReplicaCount.java

Purpose: `ECContainerReplicaCount` is the EC-specific implementation of `ContainerReplicaCount`. It classifies EC container replicas by replica index and node operational state so health checks and repair handlers can decide whether a container is under-replicated, over-replicated, unrecoverable, missing, or safe enough for decommission and maintenance transitions.

Important APIs and behavior: the constructor accepts `ContainerInfo`, current `ContainerReplica` set, pending ops, and remaining maintenance redundancy. It sorts replicas deterministically by hash, records pending add/delete indexes, validates EC replica indexes against `ECReplicationConfig.getRequiredNodes()`, and builds separate count maps for healthy, unhealthy, decommissioning/decommissioned, and maintenance replicas. Pending deletes against healthy replicas are immediately subtracted from `healthyIndexes`; pending deletes for datanodes that only have unhealthy replicas are ignored because unhealthy replicas are already excluded from healthy availability.

Control flow: `isSufficientlyReplicated(includePendingAdd)` first checks for a full set of healthy EC indexes, then allows maintenance indexes to fill the set only if enough online redundancy remains. `unavailableIndexes`, `decommissioningOnlyIndexes`, `maintenanceOnlyIndexes`, and `additionalMaintenanceCopiesNeeded` feed EC under-replication handling. `isOverReplicated(includePendingDelete)` and `overReplicatedIndexes` identify EC indexes with more than one in-service healthy copy after optional pending-delete treatment. `isUnrecoverable` requires fewer than `data` distinct available indexes; `isMissing` repeats that check with unhealthy indexes included.

State and persistence: the class is in-memory and has no persistence of its own. `addPendingOp` mutates its pending-op/index view so multi-stage handlers can account for commands scheduled earlier in the same processing pass.

Dependencies and integration: it depends on EC replication config, `ContainerReplicaOp`, datanode persisted operational state, and `NodeManager` only for the offline-check interface. It is consumed by EC health checks, EC under/over/mis handlers, and datanode admin code.

Risks: pending-delete treatment is safety-critical; double-counting deletes or applying unhealthy deletes to healthy counts can create false under-replication. The `hasFullSetOfIndexes` check only tests map size because indexes are validated on insert. EC maintenance calculations depend on `remainingMaintenanceRedundancy` being bounded correctly by the caller.

Test signals: `TestECContainerReplicaCount` covers full/missing index sets, pending add/delete effects, maintenance/decommission handling, unrecoverable and missing detection, index validation, over-replication, and offline sufficiency behavior.
