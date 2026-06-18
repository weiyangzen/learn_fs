# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/protocol/StorageContainerLocationProtocol.java

## Purpose
`StorageContainerLocationProtocol` is the broad client-facing SCM container and admin RPC contract. It covers container allocation/listing/deletion, container replicas, datanode administration, pipelines, SCM info and leadership, safe mode, replication manager, container balancer, upgrade finalization, container tokens, metrics, reconciliation, and container report suppression.

## Important APIs, Types, And Functions
The interface is `Closeable`, Kerberos-protected, and keeps `versionID = 1L` for Hadoop RPC reflection. `ADMIN_COMMAND_TYPE` identifies commands that should run on every SCM instance, while `FOLLOWER_READABLE_COMMAND_TYPES` identifies safe-mode queries that can target followers. The API uses `ContainerWithPipeline`, `ContainerInfo`, `ContainerListResult`, `Pipeline`, `ReplicationManagerReport`, `StatusAndMessages`, `Token<?>`, and many protobuf response types.

## Control Flow
As an interface, control flow is defined by method contracts. Overloads move callers from legacy replication factor APIs toward `ReplicationConfig`. Some methods are read-only lookups, while others mutate SCM state or coordinate HA/cluster operations such as decommissioning, leadership transfer, safe mode exit, and balancer start/stop.

## State, Persistence, And Dependencies
No local state exists in this file. The backing SCM implementation persists container, pipeline, node, deleted-block, secret-token, and HA state. Dependencies span `hdds` client configs, datanode and container models, protobuf command types, Apache Commons `Pair`, and Ozone upgrade types.

## Integration Points
`StorageContainerLocationProtocolClientSideTranslatorPB` implements this interface and maps each method into `StorageContainerLocationProtocolProtos.Type`. CLI/admin tools, OM, datanodes, balancer tooling, and security/token flows use this contract to communicate with SCM.

## Risks
This interface is high blast-radius: adding or changing methods requires translator, server-side, protobuf, retry/failover, and compatibility updates. Admin command routing semantics are encoded here and consumed by the translator. Deprecated methods must remain harmless for older clients.

## Test Signals
Strong tests include method-to-proto routing, all overload combinations for container listing, follower-targeted safe-mode reads, multi-SCM admin fan-out, EC and replicated allocation, token issuance, upgrade finalization status mapping, and compatibility checks for `versionID`.
