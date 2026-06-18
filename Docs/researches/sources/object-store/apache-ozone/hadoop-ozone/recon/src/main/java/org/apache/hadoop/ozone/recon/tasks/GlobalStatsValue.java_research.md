# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/GlobalStatsValue.java

Purpose: Value wrapper for RocksDB global stats rows.

Important APIs/types: immutable `Long value`, `getCodec`, `getValue`, `toProto`, `fromProto`, and `toString`.

State and persistence: serialized through a `DelegatedCodec` over `GlobalStatsValueProto`. `toProto` writes null as zero, so null and zero are indistinguishable after persistence.

Dependencies and integration: used by `ReconDBDefinition.GLOBAL_STATS` and `ReconGlobalStatsManagerImpl`. It is intended for efficient single-value stats in Recon's internal RocksDB.

Risks: no `equals`/`hashCode`, so tests or maps comparing values need to compare `getValue`. Null-to-zero conversion may hide uninitialized values. There is a parallel SQL global stats path in this code area, so metric ownership must be clear.

Test signals: codec round-trip including null, string output, and manager-level batch writes.
