# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/service/TestRootedDDSWithFSO.java

## Purpose
Integration test for `DirectoryDeletingService` when using rooted OFS paths (`ofs://om/volume/bucket/path`) with FILE_SYSTEM_OPTIMIZED buckets. It specifically validates recursive bucket and volume deletion through the rooted filesystem view.

## Important APIs and Types
The class `TestRootedDDSWithFSO` uses `MiniOzoneCluster`, `FileSystem`, `Path`, `OzoneClient`, `OzoneBucket`, `DirectoryDeletingService`, `OMMetrics`, `OMMetadataManager` tables, `OmDirectoryInfo`, `OmKeyInfo`, and the shared `TestDirectoryDeletingServiceWithFSO.assertSubPathsCount` helper.

## Control Flow
Setup starts a three-datanode cluster with FSO default bucket layout, creates a volume and bucket, configures the OFS default filesystem root, and sets a small iterate batch size. `testDeleteVolumeAndBucket` creates a tree with five two-level directory branches and six files, asserts initial table row counts, deletes the bucket path recursively, deletes the volume path non-recursively, and then polls metadata tables and deletion-service counters.

## State and Persistence
Persistent state includes FSO directory and key table rows under the volume/bucket, OM key-delete metrics, and deletion-service counters for moved files and purged dirs. The test checks that bucket and volume namespace metadata disappear from the rooted filesystem after delete.

## Dependencies and Integration Points
This bridges OFS path handling, FSO metadata layout, recursive bucket deletion, volume deletion, OM metrics, and async directory deletion service behavior.

## Risks and Edge Cases
Cleanup deletes only top-level rooted filesystem entries non-recursively, which assumes the test has already cleaned nested state. The moved-file count intentionally excludes one immediate file under the bucket because it is moved during bucket delete, so this assertion encodes detailed service behavior.

## Test Signals
Signals include rooted path deletion success, volume path becoming not found, active dir/key tables reaching zero, OM key delete metric incrementing once for bucket deletion, moved subfile count matching nested files, and deleted directory count matching total directories.
