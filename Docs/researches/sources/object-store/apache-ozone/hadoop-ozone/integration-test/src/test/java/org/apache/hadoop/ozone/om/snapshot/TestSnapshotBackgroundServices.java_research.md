# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestSnapshotBackgroundServices.java

## Purpose
`TestSnapshotBackgroundServices` exercises HA snapshot background services around follower checkpoint installation, snapshot/key deletion, compaction-log transfer, backup SST pruning, SST filtering, and snapshot diff correctness after leadership transfer.

## Important APIs, Types, and Functions
The test configures HA OM Ratis log purge/segment thresholds and service intervals for block deletion, snapshot deletion, compaction DAG pruning, and SST filtering. Key helpers are `recoverCluster`, `stopFollowerOM`, `startInactiveFollower`, `createSnapshotsEachWithNewKeys`, `getNewLeader`, `confirmSnapDiffForTwoSnapshotsDifferingBySingleKey`, `createOzoneSnapshot`, `getSnapDiffReport`, `getCompactionLogEntries`, `suspendBackupCompactionFilesPruning`, and `resumeBackupCompactionFilesPruning`.

## Control Flow, State, and Persistence
Each test recovers the 3-OM HA cluster, stops one follower, creates OBS-bucket snapshots and keys on the leader, restarts the follower so it installs a checkpoint, performs extra reads/writes, transfers leadership to that follower, and then checks service-specific state on the new leader. The deletion test verifies deleted key propagation between snapshot deleted tables after deleting an intermediate snapshot. The compaction test compares compaction log table entries and forward compaction DAG nodes/edges across old and new leaders. The pruning test suspends RocksDB checkpoint differ pruning, creates snapshots, resumes pruning, and waits for files under the SST backup directory to shrink. The SST filtering test waits for `SstFilteringService.isSstFiltered` on a new snapshot. Snapshot diff assertions validate logical correctness after background processing.

## Dependencies and Integration Points
This file integrates OM HA leadership transfer, Ratis checkpoint catch-up, OM metadata tables, RocksDB checkpoint differ and compaction DAG, SstFilteringService, snapshot deletion services, block deletion intervals, object-store bucket APIs, and asynchronous snapshot diff jobs.

## Risks and Test Signals
Risks are high because the tests rely on timing, leadership transfer, compaction side effects, and background services; one method is explicitly marked flaky. Strong signals include table membership checks, equality of compaction log/DAG state across leaders, SST backup file pruning, filtered snapshot metadata, and exact snapshot diff entries for a single key.
