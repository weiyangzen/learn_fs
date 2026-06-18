## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/ReplicationConfig.java

Purpose: common interface and factory/parser for HDDS replication configurations.

Important APIs: legacy proto type/factor factories, client type/factor factory, default resolution from config, bucket/default resolution, proto deserialization including EC, legacy factor extraction, factor adjustment for Hadoop FS compatibility, `parse` with fallback from config, `parseWithoutFallback`, and instance methods for type, required/minimum nodes, replication string, and validation format.

Control flow: parsing falls back to `ozone.replication.type` and `ozone.replication` when arguments are null. RATIS/STANDALONE parse numeric or named factors; EC delegates to `ECReplicationConfig`; all parsed configs are validated through `ReplicationConfigValidator` from the active configuration. `adjustReplication` leaves EC unchanged and reparses replicated configs from a short factor.

State/persistence: no state in the interface. Dependencies: Ozone config keys, `ConfigurationSource`, HDDS protobufs, replication implementations and validator.

Integration points: client APIs, bucket defaults, OM/SCM metadata, Hadoop filesystem replication calls, and config validation. Risks: `ReplicationType.valueOf` is case-sensitive; EC is intentionally incompatible with legacy factor APIs; validation pattern can reject otherwise parseable configs; `fromTypeAndFactor` relies on enum name matching between client and proto. Test signals: null fallback behavior, invalid type/factor messages, EC parsing, validator rejection, bucket/default precedence, and adjustReplication for EC and replicated configs.
