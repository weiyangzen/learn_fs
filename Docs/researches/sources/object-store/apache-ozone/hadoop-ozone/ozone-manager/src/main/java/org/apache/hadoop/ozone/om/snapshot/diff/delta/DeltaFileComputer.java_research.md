## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/diff/delta/DeltaFileComputer.java

Purpose: closeable strategy interface for computing SST files that can be scanned to derive table changes between two snapshots.

Important APIs and types: `Collection<Pair<Path, SstFileInfo>> getDeltaFiles(SnapshotInfo fromSnapshot, SnapshotInfo toSnapshot, Set<String> tablesToLookup) throws IOException`.

Control flow and state: no implementation; implementers may hold native resources or temp directories, hence `Closeable`.

Dependencies and integration: implemented by file-link based RDB/full/composite computers and consumed by snapshot diff and defrag logic.

Risks and test signals: callers assume returned paths are readable until `close`. Implementer tests should verify table filtering, empty-diff semantics, IOException propagation, and cleanup after close.
