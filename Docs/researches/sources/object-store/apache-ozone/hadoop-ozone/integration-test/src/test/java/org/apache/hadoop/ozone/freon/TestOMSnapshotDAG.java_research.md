# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestOMSnapshotDAG.java

## Purpose
`TestOMSnapshotDAG` is an integration test for OM snapshot diff DAG reconstruction and for the guard that skips RocksDB compaction tracking when no snapshots exist. It runs against a real `MiniOzoneCluster` and exercises Freon key generation, object-store snapshot creation, OM metadata lookup, snapshot-local SST metadata, RocksDB checkpoint differ APIs, and persistence across OM restart.

## Important APIs, Types, and Functions
- `init()` builds a three-datanode `MiniOzoneCluster`, lowers Ratis timeouts, enables filesystem snapshots, disables snapshot defrag service scheduling, and shrinks the RocksDB CF write buffer to force flush/compaction with relatively few keys.
- `getSnapshotDBKey(...)` builds the snapshot table key as `/volume/bucket/snapshot`.
- `getDifferSnapshotInfo(...)` reads `SnapshotInfo`, opens `OmSnapshotLocalDataManager` state, extracts version-to-SST-file maps, and wraps them in `DifferSnapshotVersion` for `RocksDBCheckpointDiffer`.
- `testDAGReconstruction()` creates keys through `RandomKeyGenerator`, takes snapshots `snap1`, `snap2`, and `snap3`, obtains SST diff lists for `snap2-snap1`, `snap3-snap2`, `snap3-snap1`, and `snap2-snap2`, restarts OM, and asserts the diff lists are reproduced.
- `testSkipTrackingWithZeroSnapshot()` generates enough keys to force compaction without creating snapshots, then asserts compaction log files are empty and SST backup directory has no files.

## Control Flow
The DAG test first creates initial keys and discovers the generated non-S3 volume and bucket via OM list APIs. After `snap1`, it writes 2000 zero-byte keys directly through `OzoneBucket`, creates `snap2`, pulls `OMMetadataManager`, `OmSnapshotLocalDataManager`, `RDBStore`, and `RocksDBCheckpointDiffer`, then asks the differ for pairwise SST deltas. It deletes 1000 keys, creates `snap3`, checks same-snapshot diff emptiness, closes active snapshot suppliers, restarts OM, reacquires metadata/snapshot handles, and repeats the same diff queries to prove the reconstructed DAG matches the in-memory pre-restart DAG.

## State and Persistence Behavior
The test depends on `SnapshotInfo` rows, checkpoint paths under OM metadata, snapshot-local DB transaction sequence numbers, per-version SST file metadata, compaction logs under `OM_SNAPSHOT_DIFF_DIR/DB_COMPACTION_LOG_DIR`, and SST backup files under `DB_COMPACTION_SST_BACKUP_DIR`. The restart portion verifies that DAG-related state is persisted and can be reconstructed after OM process restart, not just retained in memory.

## Dependencies and Integration Points
The file integrates Freon `RandomKeyGenerator`, Picocli command execution, Ozone client volume/bucket APIs, OM metadata tables, `OmSnapshotManager`, `OmSnapshotLocalDataManager`, `RDBStore`, and `RocksDBCheckpointDiffer`. It also depends on Ratis configuration and RocksDB compaction behavior, with logging levels adjusted for Ratis classes.

## Risks and Test Signals
Important risks are timing sensitivity around RocksDB flush/compaction, leaked active snapshot suppliers, and diff instability if SST metadata collection changes. Strong test signals are equality of diff lists before and after OM restart, empty diff for the same snapshot, successful Freon validation counts, and explicit filesystem checks showing no compaction tracking artifacts when snapshots are absent.
