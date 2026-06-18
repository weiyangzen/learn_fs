# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/replication/TestECContainerReplicaCount.java

Purpose: This suite validates `ECContainerReplicaCount`, the EC replication accounting object used to decide if an EC container is sufficiently replicated, over-replicated, missing, unrecoverable, or in need of maintenance/decommission replacement.

Important APIs and types: It uses `ECContainerReplicaCount`, `ECReplicationConfig(3,2)`, `ContainerReplica`, `ContainerReplicaOp`, `ContainerInfo`, replica indexes, `HddsProtos.NodeOperationalState` values, replica states such as `CLOSED` and `UNHEALTHY`, and helper methods from `ReplicationTestUtil`.

Control flow: Setup creates a closed EC container. Individual tests build replica sets with different index coverage, duplicate indexes, unhealthy replicas, maintenance states, decommissioning states, pending ADDs, and pending DELETEs. They instantiate `ECContainerReplicaCount` with a maintenance redundancy requirement, call methods such as `isSufficientlyReplicated`, `isOverReplicated`, `unavailableIndexes`, `overReplicatedIndexes`, `maintenanceOnlyIndexes`, `decommissioningOnlyIndexes`, `isMissing`, `isUnrecoverable`, and `isSufficientlyReplicatedForOffline`, then assert exact results.

State and persistence behavior: There is no persistence. State is derived from replica sets, pending op lists, EC data/parity indexes, operational state, replica health, and configured maintenance redundancy. Pending ops can also be added after construction with `addPendingOp`.

Dependencies and integration points: Replication manager uses this accounting to choose reconstruction, replication, deletion, maintenance, and decommission actions for EC containers. It directly affects safety decisions about whether an offline/decommissioning replica can be tolerated.

Risks: EC accounting is index-sensitive and has subtle interactions between pending deletes, pending adds, unhealthy replicas, maintenance-only copies, and decommissioned replicas. Some tests rely on duplicate replicas created with random datanodes, while equality/set behavior must preserve distinct hosts.

Test signals: Exact unavailable and over-replicated index lists, sufficient/insufficient replication with and without pending ops, maintenance copy counts capped by parity, missing vs unrecoverable distinction, decommissioning-only indexes, offline-safety checks, and pending-delete handling for unhealthy versus healthy indexes.
