<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdiff/DifferSnapshotInfo.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdiff/DifferSnapshotInfo.java

Purpose: Snapshot descriptor used by the checkpoint differ to map snapshot versions to DB paths and SST file metadata.

Important APIs/types/functions: Stores snapshot UUID, generation, a version-to-DB-path function, and a `NavigableMap<Integer,List<SstFileInfo>>`. Public methods return DB path, UUID, generation, and max version. Package-private `getSstFiles(version, tablesToLookup)` filters SST metadata by requested column families. Test-visible `getSstFile` finds one named file.

Control flow and state: The object is immutable by field reference, but it does not defensively copy the supplied map/lists. `getMaxVersion` delegates to `lastKey`, so version maps must be non-empty.

Dependencies and integration points: Used by `RocksDBCheckpointDiffer.DifferSnapshotVersion` and `getSSTDiffListWithFullPath` to build source/destination version views for DAG or full-name diffing.

Risks: Missing versions, empty maps, or null column-family values can cause runtime errors. External mutation of `versionSstFiles` can affect diff behavior.

Test signals: Diff tests should cover multi-version snapshots, table filtering, missing version maps, and path function correctness.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdiff/DifferSnapshotInfo.java -->
