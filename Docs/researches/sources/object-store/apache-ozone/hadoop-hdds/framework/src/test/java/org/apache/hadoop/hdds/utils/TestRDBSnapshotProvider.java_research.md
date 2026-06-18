<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/TestRDBSnapshotProvider.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/TestRDBSnapshotProvider.java

Purpose: tests `RDBSnapshotProvider` candidate snapshot download, incremental SST handling, DB content equivalence, cleanup on init, and leader-change consistency.

Important APIs/types/functions: `RDBSnapshotProvider`, `downloadDBSnapshotFromLeader`, `downloadSnapshot`, `getCandidateDir`, `init`, `checkLeaderConsistency`, `getInitCount`, `RDBStore`, `DBCheckpoint`, `Table`, `HAUtils.getExistingFiles`, `HddsServerUtil.writeDBCheckpointToStream`, and RocksDB managed options/statistics.

Control flow: setup creates a multi-column-family `RDBStore`, then subclasses `RDBSnapshotProvider` so `downloadSnapshot` inserts random data, takes a checkpoint, records it, and writes checkpoint files to the target stream while considering existing SST files. The download test obtains three snapshots, checks candidate directory growth, compares latest checkpoint DB contents with downloaded candidate DBs, and verifies `init` cleans the candidate directory. The leader test writes a dummy SST, changes leader IDs, and asserts reinitialization only when leader changes.

State and persistence behavior: heavy temp filesystem and RocksDB state. Candidate directories retain SSTs between downloads until init/leader-change cleanup. DB content is persisted in checkpoint directories and reopened for byte-for-byte table comparison.

Dependencies and integration points: integrates RocksDB stores/checkpoints, HA utility file detection, checkpoint streaming, file cleanup, managed RocksDB options/statistics, and codec leak detection.

Risks: RocksDB native resources and `CodecBuffer` leak detection require reliable cleanup. Random data and multiple checkpoints can be IO-heavy. Candidate directory reuse logic is high risk for HA snapshot correctness.

Test signals: asserts candidate dir existence, initial emptiness, first/second/third snapshot file-count growth, DB table equality across used column families, cleanup after `init`, leader-change init counts, dummy file deletion on new leader, no reinit for same leader, and reinit for different leader.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/TestRDBSnapshotProvider.java -->
