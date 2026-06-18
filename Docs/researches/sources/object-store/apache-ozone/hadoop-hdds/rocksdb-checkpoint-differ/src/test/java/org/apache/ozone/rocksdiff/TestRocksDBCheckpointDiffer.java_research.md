# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/ozone/rocksdiff/TestRocksDBCheckpointDiffer.java

Purpose: Main regression suite for `RocksDBCheckpointDiffer`, covering SST diff calculation, compaction DAG loading from log files and `CompactionLogEntry` rows, live RocksDB checkpoint behavior, backup pruning, value pruning, and prefix/column-family filtering.

Important APIs and types: Exercises `getSSTDiffList`, `internalGetSSTDiffList`, `processCompactionLogLine`, `addToCompactionLogTable`, `loadAllCompactionLogs`, `pruneSstFiles`, `pruneSstFileValues`, and `shouldSkipCompaction`. Uses `DifferSnapshotInfo`, `DifferSnapshotVersion`, `SstFileInfo`, `CompactionLogEntry`, `CompactionFileInfo`, `CompactionNode`, `TablePrefixInfo`, managed RocksDB wrappers, and Mockito.

Control flow: `init` creates clean active DB, metadata, compaction-log, and backup directories, mocks config, creates the differ with lock callbacks, opens RocksDB column families, and loads logs. Parameterized no-DB cases build synthetic DAGs and compare same/diff SST sets. The DB-backed test writes many keys, checkpoints, traverses the graph, validates deterministic snapshot diffs, and checks backup links.

State and persistence behavior: The suite creates real RocksDB state, checkpoint directories, a compaction log table, backup SSTs, and temporary pruned files. It verifies persisted compaction entries, deletion of consumed log files, and metrics/state changes during pruning.

Dependencies and integration points: Integrates RocksDB JNI, Ozone managed DB wrappers, compaction-log codecs, Guava graphs, Ozone config keys, and table prefix metadata.

Risks: DB-backed expectations depend on RocksDB compaction naming/order and are marked flaky. Prefix filtering is conservative when metadata is missing. Lock tests protect pruning from racing with bootstrap.

Test signals: Strong signals include parameterized DAG expansion, pruning scenarios, pruning metrics, `shouldSkipNode` edge cases, desired-column-family DAG checks, and `shouldSkipCompaction` cases.
