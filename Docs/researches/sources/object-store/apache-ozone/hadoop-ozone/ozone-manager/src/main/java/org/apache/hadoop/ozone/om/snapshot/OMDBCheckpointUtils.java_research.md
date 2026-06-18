# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/OMDBCheckpointUtils.java

Purpose: `OMDBCheckpointUtils` contains utility methods for OM DB checkpoint transfer behavior, especially snapshot-data inclusion and tarball size estimation.

Important APIs and types: `includeSnapshotData(HttpServletRequest)` reads the `OZONE_DB_CHECKPOINT_INCLUDE_SNAPSHOT_DATA` request parameter and parses it as a boolean. `logEstimatedTarballSize(Path dbLocation, Collection<Path> snapshotPaths)` counts SST files and byte size under the active DB path and optionally supplied snapshot paths.

Control flow: `logEstimatedTarballSize()` creates Commons IO path counters and a `CountingPathVisitor` configured with an SST suffix file filter and a directory-true filter. It walks the DB location, then walks each snapshot directory when the collection is non-empty, and logs total kilobytes, file count, and snapshot count. Exceptions are caught and logged; checkpoint streaming should not fail solely because estimation failed.

State and persistence behavior: no state is written. The utility performs filesystem reads only.

Dependencies and integration points: it depends on servlet requests, Commons IO file visitors, `ROCKSDB_SST_SUFFIX`, and `OZONE_DB_CHECKPOINT_INCLUDE_SNAPSHOT_DATA`. It is likely used by OM DB checkpoint servlet or transfer code when snapshot SST data can be included in checkpoint downloads.

Risks: the byte count is an estimate over files matching the SST filter; it may not account for hardlink de-duplication or files created/deleted during traversal. Logging errors instead of propagating them is intentional but can hide repeated filesystem permission problems unless logs are monitored.

Test signals: checkpoint servlet integration tests, especially inode-based transfer tests, are the expected coverage area.
