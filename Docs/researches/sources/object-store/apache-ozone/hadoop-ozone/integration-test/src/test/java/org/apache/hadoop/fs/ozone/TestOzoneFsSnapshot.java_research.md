# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFsSnapshot.java

Purpose: integration suite for `ozone fs` snapshot CRUD and snapshot listing semantics through OFS against an HA-style mini cluster with snapshots enabled.

Important APIs/types/functions: setup enables filesystem snapshots, short snapshot-deletion interval, disabled SST filtering, larger listing max/page sizes, and disabled snapshot rename; creates volume, bucket, and key through `OzoneFsShell`. Tests cover duplicate snapshot names, subdirectory input normalization, valid/invalid snapshot names and paths, blocked rename through object-store API and CLI, `.snapshot` listing with deleted snapshots filtered out, snapshot key listing, bucket deletion blocked by snapshots, delete success/failure, and snapshot name reuse. Helpers `execShellCommandAndGetOutput` and `createSnapshot` wrap shell execution and wait for snapshot DB/directory state.

Control flow: most tests issue shell commands with `ToolRunner.run(shell, args)` and assert exit codes plus stdout/stderr. Some tests inspect `SnapshotInfoTable` directly to avoid race with DB flush. Listing tests pause `SnapshotDeletingService`, create multiple snapshots beyond page size, delete one, wait for `SNAPSHOT_DELETED`, and confirm only active snapshots are listed.

State and persistence behavior: snapshots are persisted in OM metadata and on-disk snapshot directories. Deleted snapshots can remain in metadata while marked deleted and must be hidden from filesystem listing. Existing snapshots prevent bucket deletion while preserving snapshot-visible keys after live keys are removed. Rename is blocked by OM config and returns `FEATURE_NOT_ENABLED`.

Dependencies and integration points: uses `MiniOzoneCluster.newHABuilder`, `OzoneFsShell`, `OzoneShell`, `OzoneClient.renameSnapshot`, `SnapshotInfo`, `OmSnapshotManager.getSnapshotPath`, snapshot/deleting services, and shell output capture.

Risks: helper restores `System.out/err` to new print streams over byte arrays, so it is suitable for test isolation but fragile in shared output contexts. Snapshot deletion and directory materialization are asynchronous and guarded by waits. Assertions depend on CLI messages and page-size configuration.

Test signals: catches snapshot validation regressions, path normalization bugs for subdirectory inputs, deleted snapshot leakage in listings, broken snapshot key access, bucket-deletion safety violations, rename feature-gate bypass, and snapshot-name reuse failures.
