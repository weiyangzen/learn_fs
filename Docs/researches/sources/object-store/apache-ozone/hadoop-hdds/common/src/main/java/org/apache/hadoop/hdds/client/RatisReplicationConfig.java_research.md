## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/RatisReplicationConfig.java

Purpose: immutable `ReplicationConfig` for RATIS replication.

Important APIs: static cached `getInstance` for ONE and THREE, `hasFactor`, `getReplicationType`, `getRequiredNodes`, `getReplicationFactor`, `getReplication`, `configFormat`, `getMinimumNodes`, equality/hash/toString.

Control flow: returns shared instances for common factors, creates a new instance for other proto enum values if ever provided. State/persistence: final factor; JSON exposes `replicationType` as enum via `@JsonProperty`.

Dependencies: HDDS protobuf enum types, Jackson, JCIP immutable. Integration points: `ReplicationConfig` parsing, bucket defaults, OM/SCM validation, client JSON. Risks: `getRequiredNodes` calls protobuf `getNumber`, which is not the same API as client `ReplicationFactor.getValue` but works for known proto enum numeric values; unsupported factors can be constructed if proto enum expands. Test signals: singleton behavior for ONE/THREE, JSON property, legacy factor extraction, minimum node behavior, and validation against allowed-config regex.
