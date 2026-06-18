# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/SstFilteringService.java

Purpose: `SstFilteringService` is a single-threaded background service that removes irrelevant RocksDB SST files from snapshot directories. It reduces snapshot footprint by deleting files whose prefixes do not correspond to the snapshotted bucket, and marks snapshots as filtered.

Important APIs and types: It extends `BackgroundService` and implements `BootstrapStateHandler`. Key public elements are `SST_FILTERED_FILE`, `isSstFiltered`, `start`, test-only `pause` and `resume`, `getTasks`, `getSnapshotFilteredCount`, `getBootstrapStateLock`, and `shutdown`. The inner `SstFilteringTask` performs the actual iteration.

Control flow: Each task scans `snapshotInfoTable` from the beginning while the per-task limit remains and the service is running. It skips already-filtered snapshots and snapshots whose local data version indicates defrag already handled filtering. For each eligible snapshot, it computes the bucket table-prefix set, acquires the bootstrap read lock, opens the active snapshot, calls `RocksDatabase.deleteFilesNotMatchingPrefix`, writes an `sstFiltered` marker file under the snapshot directory while holding `SNAPSHOT_DB_LOCK` read lock, decrements the limit, and increments the filtered count. Deleted snapshots and missing active snapshots are handled specially to avoid noisy failures.

State and persistence behavior: Durable effects are deletion of SST files from snapshot RocksDB directories and creation of the marker file. SnapshotInfo's own `isSstFiltered` field may also be consulted if updated elsewhere. Runtime state includes `running`, `snapshotFilteredCount`, and bootstrap lock wrapper state.

Dependencies and integration points: It integrates with `OmSnapshotManager`, `OmSnapshotLocalDataManager`, OM metadata tables, RocksDB prefix filtering, `SNAPSHOT_DB_LOCK`, and bootstrap state locking.

Risks and test signals: Incorrect prefix computation or lock ordering could delete needed snapshot SST files or race with snapshot deletion/defrag. The task scans from the start each cycle, so many already-filtered snapshots can create repeated iteration cost. Tests should cover marker detection, defrag skip, deleted-midway handling, batch limit enforcement, pause/resume, bootstrap lock use, and that filtered snapshot DBs still serve relevant bucket metadata.
