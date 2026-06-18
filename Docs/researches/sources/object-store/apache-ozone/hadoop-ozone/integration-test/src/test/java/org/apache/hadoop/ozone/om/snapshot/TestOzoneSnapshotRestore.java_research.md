# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOzoneSnapshotRestore.java

## Purpose
`TestOzoneSnapshotRestore` validates restore-like workflows where keys are copied out of Ozone snapshot paths back into live buckets using `OzoneFsShell -cp`. It covers FSO and legacy bucket layouts, cross-bucket restores, cross-layout restores, and restoration after non-contiguous snapshot deletion.

## Important APIs, Types, and Functions
The test enables `OZONE_FILESYSTEM_SNAPSHOT_ENABLED_KEY`, starts a 3-OM HA cluster, configures OFS via `FS_DEFAULT_NAME_KEY`, and uses `ObjectStore.createSnapshot`, `OmSnapshotManager.getSnapshotPrefix`, `OmSnapshotManager.getSnapshotPath`, and `OzoneFsShell`. Helpers include `createFileKey`, `deleteKeys`, `createSnapshot`, `keyCount`, `keyCopy`, and `waitForKeyCount`. Test cases are parameterized by `BucketLayout.FILE_SYSTEM_OPTIMIZED` and `BucketLayout.LEGACY`, plus mixed source/destination layout pairs.

## Control Flow, State, and Persistence
`init` stops the leader `KeyManagerImpl` deletion services so deleted data remains readable during restore tests. Each test creates volumes, buckets, keys, and a snapshot, waits for the snapshot checkpoint `CURRENT` directory to appear on disk, then uses OFS absolute paths containing the snapshot prefix to copy snapshot keys into a destination bucket. `testUnorderedDeletion` creates ten incremental snapshots, deletes every third snapshot starting at index two, deletes live keys, and restores from the latest snapshot to confirm snapshot chains still expose retained key versions.

## Dependencies and Integration Points
The tests tie together OM snapshot metadata, filesystem snapshot path construction, OFS shell copy semantics, bucket layout translation, key listing, and snapshot checkpoint persistence. They depend on the mini-cluster's client config and on the snapshot directory naming contract used by `OmSnapshotManager`.

## Risks and Test Signals
Risks include asynchronous checkpoint creation, delayed key visibility, deletion services removing data before copy, and known RocksDB seek behavior noted in the cross-bucket test. Test signals are key counts before and after deletion/copy and zero exit codes from the filesystem shell. Coverage focuses on observable restore behavior, not on a first-class restore API.
