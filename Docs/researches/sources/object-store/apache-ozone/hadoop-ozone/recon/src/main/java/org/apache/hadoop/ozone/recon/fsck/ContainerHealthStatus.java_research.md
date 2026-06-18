## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/fsck/ContainerHealthStatus.java

Purpose: value object that computes health, replication, placement, checksum, and key-count signals for a container and its replicas.

Important APIs/types/functions: constructor derives healthy replica sets, placement status, replica delta, key count, and `ContainerReplicaCount`; getters expose container ID/info, replication factor/count, missing/empty/deleted/over/under/mis-replicated checks, placement deltas/reasons, and checksum mismatch detection.

Control flow: unhealthy replicas are excluded from healthy sets; decommissioned/maintenance nodes are excluded from available replicas; placement is validated with healthy replicas. Ratis and EC containers instantiate different `ContainerReplicaCount` implementations using `ReplicationManagerConfiguration`.

State and persistence: no writes, but reads key count through `ReconContainerMetadataManager`. It integrates with placement policy, SCM container model, replica-count classes, and Recon metadata.

Risks: `getContainerKeyCount` wraps `IOException` as unchecked `RuntimeException`; `areChecksumsMismatched` compares `ContainerReplica::getChecksums`, while `ReconReplicationManager` uses data checksum. Tests should cover EC/Ratis differences, maintenance/decommission filtering, missing/empty logic, placement policy results, key-count failure, and checksum mismatch semantics.
