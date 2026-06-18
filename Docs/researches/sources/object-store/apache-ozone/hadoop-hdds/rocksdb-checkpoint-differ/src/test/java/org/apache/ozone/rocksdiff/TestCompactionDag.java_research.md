<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/ozone/rocksdiff/TestCompactionDag.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/ozone/rocksdiff/TestCompactionDag.java

Purpose: End-to-end and structural tests for compaction DAG pruning, legacy compaction log migration, compaction log table loading, and bootstrap-lock interaction.

Important APIs/types/functions: The fixture creates temp-ish active DB, metadata, compaction log, and SST backup directories; configures a `RocksDBCheckpointDiffer` with mocked configuration and a `ReadWriteLock`-backed bootstrap lock; opens a managed RocksDB with checkpoint-differ listeners and compaction log column family. Helpers build synthetic forward/backward Guava graphs from SST levels, count compaction log table entries, and assert lock blocking behavior.

Control flow and state: Parameterized prune scenarios construct expected graph states after removing levels from backward or forward DAGs. End-to-end scenarios write legacy text log files or direct compaction table entries, call `loadAllCompactionLogs`, assert pre-prune table counts, run `pruneOlderSnapshotsWithCompactionHistory` while verifying it waits for a held write lock, then assert remaining graph nodes, deleted legacy log files, and post-prune table counts.

Dependencies and integration points: Covers `CompactionDag`, `RocksDBCheckpointDiffer`, `CompactionLogEntry`, managed RocksDB column families, native library load mocking, Ozone config keys, and bootstrap state locking.

Risks: Uses fixed relative directory names under the test working directory, so cleanup correctness matters. The graph factories encode expected direction conventions; if direction names change, test readability could suffer even if behavior remains.

Test signals: Strong coverage of forward/backward graph pruning, old text log formats with snapshot lines and missing snapshots, direct table entries, aged compaction time pruning, legacy log deletion after migration, table entry deletion, and lock acquisition semantics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/ozone/rocksdiff/TestCompactionDag.java -->
