<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/ozone/compaction/log/TestCompactionFileInfo.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/ozone/compaction/log/TestCompactionFileInfo.java

Purpose: Parameterized tests for `CompactionFileInfo` builder validation, prune state, and protobuf serialization.

Important APIs/types/functions: Scenario providers define valid all-fields and file-name-only cases plus invalid partial metadata combinations. Tests cover `Builder`, `setPruned`, `getProtobuf`, and `getFromProtobuf`.

Control flow and state: Valid scenarios build objects, verify initial and mutated pruned state, and then verify protobuf optional field presence. Invalid scenarios assert exact exception messages for null file name or incomplete start/end/column-family triples. From-protobuf tests also check explicit false and true pruned flags.

Dependencies and integration points: Protects the persisted file-info contract consumed by `CompactionLogEntry`, DAG population, and prefix filtering.

Risks: Exact exception message assertions can be brittle under message refactors. Duplicate valid scenario entries add no new coverage.

Test signals: Strong validation for all-or-none metadata, optional protobuf fields, and pruned flag round trip.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/ozone/compaction/log/TestCompactionFileInfo.java -->
