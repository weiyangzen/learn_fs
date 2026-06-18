## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/ReplicatedReplicationConfig.java

Purpose: marker-style interface for replication schemes that copy data by a factor, such as RATIS and STANDALONE.

Important API: `getReplicationFactor()` returns the HDDS protobuf replication factor. Control flow/state: none. Dependencies: `ReplicationConfig` and HDDS protobufs.

Integration points: `ReplicationConfig.getLegacyFactor`, `DefaultReplicationConfig.toProto`, and code paths that need factor-based behavior only for replicated schemes. Risks: implementors must ensure `getReplicationFactor`, `getRequiredNodes`, and config format remain consistent. Test signals: interface coverage for all replicated implementations and non-EC legacy serialization.
