# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OMDBCheckpointServlet.java

## Purpose
`OMDBCheckpointServlet` exposes the current OM DB checkpoint as a tar archive for bootstrap and metadata synchronization. It extends the generic `DBCheckpointServlet` with OM-specific authorization, leadership checks, snapshot DB inclusion, RocksDB SST deduplication, follower-provided SST exclusion, hardlink metadata, transfer size limiting, and bootstrap locking.

## Important APIs, types, and functions
`init` obtains `OzoneManager` from servlet context, builds allowed admin users/groups plus Recon principal, initializes the superclass with the OM DB store and DB checkpoint metrics, and installs an OM-specific bootstrap `Lock`. `processMetadataSnapshotRequest` refuses requests unless the OM is leader-ready. `writeDbDataToStream` drives archive creation. `getCheckpoint` creates a RocksDB checkpoint and snapshots compaction log and SST backup directories into a temp area. `normalizeExcludeList`, `getFilesForArchive`, `processDir`, `processFile`, `findLinkPath`, and `writeFilesToArchive` implement file selection and streaming. The nested `DirectoryData` represents original and temp copies of RocksDB support directories; nested `Lock` waits for double-buffer flush before acquiring `BOOTSTRAP_LOCK`.

## Control flow
For an accepted request, the superclass creates or obtains a checkpoint and calls `writeDbDataToStream`. The servlet creates temporary views of the SST backup and compaction log directories from the RocksDB checkpoint differ. It normalizes follower-supplied excluded SST paths so they can be compared against leader-side checkpoint, snapshot, and temp backup paths. `getFilesForArchive` sets the max total SST size from configuration, disables the limit when snapshot data is not requested, optionally logs an estimated tarball size, processes active checkpoint files, and, if snapshots are included, processes expected snapshot directories, copied SST backup files, and copied compaction logs.

`processDir` recursively walks directories, skipping unexpected snapshot checkpoint directories, real compaction log directories, and real SST backup directories when processing broader trees. For files, `processFile` decides whether to skip an excluded file, emit it as a hardlink to an already-known path, or include the file in the tarball. SST files are deduplicated by filename plus inode comparison through `findLinkPath`; non-SST files are copied directly. A cumulative SST byte counter can stop processing early, causing an incomplete tarball batch.

`writeFilesToArchive` writes either all selected files or only SST files when the transfer is incomplete. It verifies destination paths are under the metadata directory, rewrites checkpoint file names to tar root, includes files, logs progress, and, for a completed transfer, writes the hardlink list and Ratis snapshot complete marker.

## State and persistence behavior
The servlet reads OM DB checkpoint files, snapshot DB directories, compaction logs, and SST backup files. It creates temporary copies/hardlinks under the request temp directory, but it does not mutate OM metadata state. It relies on checkpoint-local `SnapshotInfo` table reads to identify snapshot directories and can wait for snapshot directories to appear. The bootstrap lock ensures checkpoint transfer is coordinated with OM state transitions; the write lock waits for the double buffer to flush before locking.

## Dependencies and integration points
It integrates with `OzoneManager`, `RDBStore`, `RocksDBCheckpointDiffer`, `OmMetadataManagerImpl`, `OmSnapshotLocalDataManager`, `OMDBCheckpointUtils`, `OmSnapshotUtils`, `DBCheckpointMetrics`, Recon config, SPNEGO/admin authorization in the superclass, and Ratis snapshot transfer markers. The follower side depends on the hardlink file and complete marker to reconstruct incremental SST transfer correctly.

## Risks and edge cases
Path normalization is subtle because excluded follower paths may refer to active DB, snapshot DB, or temporary backup locations. Incorrect `metaDirPath` derivation or destination validation can either reject valid files or include files with wrong tar paths. `processDir` materializes `Files.list(dir)` into a list before iterating, which reduces stream lifetime issues but can consume memory for huge directories. The max SST size gate can produce partial tarballs containing only SST files until the final batch. SnapshotInfo may reference a directory not yet present, so `waitForDirToExist` can fail the request. Hardlink detection uses inode comparison and logs same-name non-linked SSTs.

## Test signals
Tests should cover admin/recon authorization initialization, non-leader rejection, exclude-list normalization for active, snapshot, and backup paths, `processFile` copy/link/skip behavior, same-name non-hardlinked SST behavior, max SST size partial transfer, snapshot directory filtering, compaction/backup directory skipping, completed versus incomplete archive contents, and bootstrap lock waiting for double-buffer flush.
