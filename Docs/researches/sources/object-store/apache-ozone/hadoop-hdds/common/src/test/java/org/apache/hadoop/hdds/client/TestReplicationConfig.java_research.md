# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/client/TestReplicationConfig.java

## Purpose
`TestReplicationConfig` exercises the main replication configuration factory surface for replicated and erasure-coded modes. It verifies defaults, parsing, protobuf deserialization, string rendering, replication adjustment, and validation against allowed config patterns.

## APIs and dependencies
The class targets `ReplicationConfig`, `RatisReplicationConfig`, `StandaloneReplicationConfig`, `ECReplicationConfig`, replicated `ReplicationType` and `ReplicationFactor`, protobuf `HddsProtos`, `ConfigurationSource`, and `OzoneConfiguration`. It uses `ozone.replication`, `ozone.replication.type`, and `ozone.replication.allowed-configs`.

## Control flow and state behavior
Parameterized sources define RATIS/STAND_ALONE with ONE/THREE factors and EC RS layouts with 3-2, 6-3, and 10-4 data/parity combinations using 1 MB or 2 MB chunks. Default config falls back to RATIS/THREE when unset. Parsing from config values and string values builds the correct subclass. Protobuf helpers recreate configs from proto fields. `getReplication()` returns factor names for replicated configs and canonical EC descriptors with `k` suffixes. `adjustReplication` changes replicated factors for filesystem callers but leaves EC configs unchanged. Validation-enabled paths reject disallowed configs for parse/default/adjust while direct construction from proto or Java objects remains allowed for old persisted keys.

## Integration points
Replication config is central to bucket defaults, key creation, filesystem replication adjustment, persisted protobuf metadata, and compatibility with keys written under older policies.

## Risks and test signals
The test protects default behavior, string/proto compatibility, EC descriptor units, and the important distinction between new-write validation and old-key deserialization. Policy regex changes are risky because `STANDALONE/ONE|RATIS/THREE` style patterns gate user-visible replication choices.
