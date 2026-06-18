<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/KeyDeletingService.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/KeyDeletingService.java

Purpose: Background service that reclaims deleted key blocks through SCM and then purges or updates OM deleted-key metadata, including snapshot deep-cleaning flows.

Important APIs/types/functions: Extends `AbstractKeyDeletingService`. Important state includes `ScmBlockLocationProtocol`, key limit, deleted-key counter, deep-clean flag, snapshot chain manager, Ratis byte limit, and per-run `DeletionStats`. Key methods include `processKeyDeletes`, `submitPurgeKeysRequest`, `getPurgeKeysRequest`, `submitPurgeRequest`, `execTaskCompletion`, `resetMetrics`, `getTasks`, and nested `KeyDeletingTask`.

Control flow and persistence: Tasks run only on leader-ready OM. They process AOS plus optional snapshots, skipping already deep-cleaned snapshots, snapshots whose DB changes are unflushed, snapshots whose directory deep-clean is incomplete, and AOS when the previous purge transaction is not flushed. `processDeletedKeysForStore` filters reclaimable deleted keys and rename entries, validates expected previous snapshot ID, sends non-empty block groups to SCM, treats empty files as successfully deleted without SCM calls, then submits `PurgeKeys` requests. The purge request batches deleted key names, key-version updates, renamed-key deletions, and per-bucket purged byte/namespace deltas under the Ratis byte budget.

Dependencies and integration: Integrates OM `KeyManager`, SCM block deletion, snapshot filters, snapshot chain manager, metrics, tracing, and OM Ratis purge request handling.

Risks and test signals: Block deletion must precede OM purge to avoid orphan blocks, and failed block groups must prevent metadata purge for all versions of that key. Tests should cover empty-file deletion, partial SCM failures, keys-to-modify versions, renamed entries, Ratis splitting, bucket purge size accounting, snapshot deep-clean sequencing after directory cleanup, exclusive size updates, and retry/idempotency.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/KeyDeletingService.java -->
