<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/ozone/compaction/log/TestCompactionLogEntry.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/ozone/compaction/log/TestCompactionLogEntry.java

Purpose: Parameterized tests for `CompactionLogEntry` protobuf serialization and deserialization.

Important APIs/types/functions: Scenario provider builds common input/output `CompactionFileInfo` lists and runs cases with and without `compactionReason`. Tests use `CompactionLogEntry.Builder`, `getProtobuf`, and `getFromProtobuf`.

Control flow and state: The serialization test builds an entry, converts it to proto, checks sequence/time, maps nested file-info protos back to objects, and verifies optional reason presence. The deserialization test manually builds the proto, deserializes, and checks all fields and nested lists.

Dependencies and integration points: Protects the compaction log table value format used by `RocksDBCheckpointDiffer` for DAG reconstruction and pruning metadata updates.

Risks: Does not cover `toBuilder`, `copyObject`, equality/hash code, or updated input list after pruning. Lists are reused across scenarios, so deep-copy behavior is not tested.

Test signals: Confirms nested file info lists and optional compaction reason survive proto round trips.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/ozone/compaction/log/TestCompactionLogEntry.java -->
