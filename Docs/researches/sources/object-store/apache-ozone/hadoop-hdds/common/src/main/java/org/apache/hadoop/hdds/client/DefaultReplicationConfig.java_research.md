## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/client/DefaultReplicationConfig.java

Purpose: wrapper for the default replication configuration stored in protocol objects, covering EC and replicated modes.

Important APIs: constructor from any `ReplicationConfig`, `fromProto`, `getType`, `getReplicationConfig`, `toProto`, equality/hash/toString. `toProto` writes an EC submessage for EC configs and legacy type/factor for replicated configs.

Control flow: `fromProto` rejects null, branches on `hasEcReplicationConfig`, otherwise delegates legacy type/factor parsing. State/persistence: immutable references, but wrapped config mutability depends on implementation.

Dependencies: HDDS protobufs and replication config classes. Integration points: bucket/volume/default replication serialization. Risks: non-EC `toProto` derives factor from `getRequiredNodes`, so unsupported node counts throw through `ReplicationFactor.valueOf`; EC field presence controls parsing, so inconsistent proto type and EC payload can surprise consumers. Test signals: EC and RATIS/STANDALONE proto round trips, null proto rejection, equality across wrapped configs, and invalid required node count.
