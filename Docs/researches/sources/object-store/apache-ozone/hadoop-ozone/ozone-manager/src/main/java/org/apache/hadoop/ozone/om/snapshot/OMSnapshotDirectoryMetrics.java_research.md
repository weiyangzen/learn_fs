# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/OMSnapshotDirectoryMetrics.java

Purpose: `OMSnapshotDirectoryMetrics` is an `OMPeriodicMetrics` and Hadoop `MetricsSource` implementation that tracks disk usage and SST counts for the `db.snapshots` directory and the SST backup directory.

Important APIs and types: `create()` registers the metrics source with `DefaultMetricsSystem`. `updateMetrics()` performs synchronous refresh. `getMetrics()` emits gauges. Test-visible getters expose cached gauge values. `unRegister()` stops the periodic scheduler and unregisters the source. `SnapshotMetricsInfo` enumerates metric names and descriptions.

Control flow: on each update, the class verifies the metadata store is an `RDBStore`, obtains `snapshotsParentDir`, validates that it exists as a directory, obtains the optional RocksDB checkpoint differ SST backup directory, and calls `calculateAndUpdateMetrics()`. Invalid or failing conditions call `resetMetrics()` and return false. `calculateAndUpdateMetrics()` lists immediate snapshot checkpoint directories, counts each as one snapshot, and calls `calculateDirSize()` for each. Backup directory size/count is calculated separately.

State and persistence behavior: the class only updates in-memory `MutableGaugeLong` metrics. It does not persist state. To avoid double-counting hardlinked snapshot SST files, it tracks visited inode/file keys across snapshot directories. If inode retrieval is unsupported or fails, it falls back to path-plus-size or direct file size counting.

Dependencies and integration points: it depends on OM metadata store APIs, `RDBStore`, `RocksDBCheckpointDiffer`, `IOUtils.getINode()`, Hadoop metrics2, and `ROCKSDB_SST_SUFFIX`. It reports operational signals for snapshot storage growth and backup SST retention.

Risks: `calculateDirSize()` only lists one directory level and does not recursively walk subdirectories; this is probably aligned with RocksDB checkpoint SST layout but should be revisited if checkpoint structure changes. It collects stream contents to lists before iteration, trading simplicity for extra memory. The inode fallback can overcount hardlinks on filesystems without inode support.

Test signals: direct tests should assert reset behavior, inode de-duplication, SST suffix filtering, backup directory counting, and unregister behavior. Checkpoint servlet/inode transfer integration tests also provide indirect signals.
