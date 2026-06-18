<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/DirectoryDeletingService.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/DirectoryDeletingService.java

Purpose: Background service that purges FSO deleted directories and moves child files/directories into deletion tables, for both the active object store and optionally deep-clean-enabled snapshots.

Important APIs/types/functions: Extends `AbstractKeyDeletingService`. Important state includes Ratis byte limit, snapshot chain manager, deep-clean flag, reconfigurable deletion thread pool, per-run metrics, and `pathLimitPerTask`. Key methods include `registerReconfigCallbacks`, `updateAndRestart`, `getTasks`, `execTaskCompletion`, `shutdown`, `start`, `optimizeDirDeletesAndSubmitRequest`, `prepareDeleteDirRequest`, `wrapPurgeRequest`, `submitPurgePathsWithBatching`, and `submitPurgeRequest`. Nested `DirDeletingTask` handles AOS or one snapshot.

Control flow and persistence: Each run queues an AOS deletion task and, if configured, one task per snapshot. Tasks skip non-leader states, already deep-cleaned snapshots, unflushed snapshot changes, and AOS work whose previous purge transaction is not flushed. Processing uses `ReclaimableDirFilter` and `ReclaimableKeyFilter`, scans deleted directory entries, discovers subdirectories and subfiles, strips ACLs from moved records, builds `PurgeDirectories` requests under a Ratis size budget, includes expected previous snapshot ID and bucket-name info, and submits through OM Ratis. When all snapshot entries are processed it submits `SetSnapshotProperty` updates for exclusive size deltas and deep-clean flags.

Dependencies and integration: Depends on `KeyManager` pending-deletion scans, snapshot chain utilities, OM locks, Ratis request submission, deletion/performance metrics, reconfiguration callbacks, and protobuf purge request types.

Risks and test signals: Race protection around snapshot chain changes and request size batching is critical. Tests should cover AOS and snapshot paths, deep-clean skip flags, unflushed snapshot gating, reconfiguration restart without deadlock, recursive directory deletion limits, Ratis batch splitting, expected-previous-snapshot validation, exclusive size updates, and retry after failed submit.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/DirectoryDeletingService.java -->
