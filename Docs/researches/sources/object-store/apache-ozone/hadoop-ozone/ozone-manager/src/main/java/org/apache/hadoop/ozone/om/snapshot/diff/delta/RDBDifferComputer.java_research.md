## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/diff/delta/RDBDifferComputer.java

Purpose: efficient delta strategy backed by `RocksDBCheckpointDiffer`, using snapshot local version metadata and the compaction DAG to identify changed SSTs.

Important APIs and types: package-private subclass of `FileLinkDeltaFileComputer`; overrides `computeDeltaFiles`; helper `toDifferSnapshotInfo` converts `SnapshotInfo` and `OmSnapshotLocalData` to `DifferSnapshotInfo`.

Control flow: obtains the active metadata store's checkpoint differ. For the target snapshot, opens local data resolved against the from-snapshot, constructs differ snapshot descriptors for both ends, builds a map from current version to previous snapshot version, synchronizes on the differ, asks for a full-path SST diff list filtered by table prefix and table names, and hard-links each returned path.

State and persistence: reads `OmSnapshotLocalData` version/SST metadata; creates temporary hard links; does not mutate durable state.

Dependencies and integration: used by `CompositeDeltaDiffComputer` when partial differ is enabled. Depends on correctly maintained snapshot version metadata from snapshot creation/defrag and on active `RocksDBCheckpointDiffer`.

Risks and test signals: missing previous snapshot local data or empty version maps turn into IO failures and cause composite fallback. Synchronization serializes differ use across callers. Tests should cover null differ, missing previous local data, empty versions, version-map construction, table filtering, synchronized differ invocation, and link creation for each returned SST.
