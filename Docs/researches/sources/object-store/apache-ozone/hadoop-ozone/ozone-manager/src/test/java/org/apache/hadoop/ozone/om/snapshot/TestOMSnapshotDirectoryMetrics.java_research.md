# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOMSnapshotDirectoryMetrics.java

Purpose: Tests `OMSnapshotDirectoryMetrics` filesystem scanning for snapshot directories and SST backup directories. Important APIs and types include `OMMetadataManager`, mocked `RDBStore`, mocked `RocksDBCheckpointDiffer`, `OzoneConfiguration`, `ROCKSDB_SST_SUFFIX`, Java `Files`, and hardlink creation.

Control flow: Setup points mocked store methods at temporary snapshot and backup directories. The test creates one snapshot directory with one `.sst` file, two backup `.sst` files, updates metrics, and asserts snapshot count, SST counts, and sizes. It then creates a second snapshot with a hardlink to the first SST file, updates metrics again, and expects deduplicated snapshot SST count/size. Finally it adds a non-SST backup file and verifies backup directory size includes it while backup SST count stays unchanged.

State and persistence behavior: Uses real temporary filesystem files and links, but no OM DB data. Metrics state is recomputed from directory contents.

Dependencies and integration points: Snapshot checkpoint directory layout, SST suffix filtering, hardlink-aware size/count handling, and checkpoint differ backup path. Risks include filesystems without hardlink support, handled by fallback write. Test signals are exact metric counts and byte totals after each update.
