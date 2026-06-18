# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestSnapshotDirectoryCleaningService.java

## Purpose
`TestSnapshotDirectoryCleaningService` validates snapshot deep cleaning for FSO directories, including exclusive size accounting and snapshot diff correctness after deleted directories have been deep-cleaned.

## Important APIs, Types, and Functions
The test enables `OZONE_SNAPSHOT_DEEP_CLEANING_ENABLED`, ACLs, low directory/block deleting intervals, and small `OZONE_FS_ITERATE_BATCH_SIZE`. It uses `FileSystem` over an FSO bucket, OM metadata tables (`deletedDirTable`, key table, directory table, deleted key table, snapshot info table), `DirectoryDeletingService`, `SnapshotChainManager`, `SnapshotUtils.getNextSnapshot`, and `ObjectStore.snapshotDiff`.

## Control Flow, State, and Persistence
`testExclusiveSizeWithDirectoryDeepClean` creates nested directory/file trees, snapshots them, adds more files, deletes a subtree and root files, creates more snapshots, waits for directory deletion service runs, and verifies each snapshot's exclusive size plus deep-cleaning delta. Because replication is RATIS/THREE, replicated exclusive size is expected to be three times logical size. `testSnapshotDiffBeforeAndAfterDeepCleaning` suspends deletion services, deletes a directory, snapshots, resumes services, waits for deep cleaning flags on `snap1`, creates a later snapshot, and verifies the diff from `snap2` to `snap3` reports the expected directory creations.

## Dependencies and Integration Points
This file ties FSO namespace operations, OM metadata tables, directory/key deletion background services, snapshot chain traversal, exclusive size accounting, replicated size accounting, and snapshot diff. It depends on asynchronous service progress and direct metadata table row counts.

## Risks and Test Signals
Risks include timing sensitivity, deep-cleaning flags lagging table changes, and brittle expected table row counts. One size test is marked flaky. Test signals include exact table counts, snapshot deep-cleaned flags, exclusive size totals, replicated size totals, and exact snapshot diff entries.
