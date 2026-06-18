<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/AbstractKeyDeletingService.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/AbstractKeyDeletingService.java

Purpose: Shared base for OM deletion background services such as key, directory, and snapshot deletion. It centralizes leader readiness checks, bootstrap locking, request submission through Ratis, metrics access, suspension, and snapshot-property request submission.

Important APIs/types/functions: Extends `BackgroundService` and implements `BootstrapStateHandler`. Important methods are abstract `getTasks`, `submitRequest`, `shouldRun`, `isPreviousPurgeTransactionFlushed`, `suspend`, `resume`, `isBufferLimitCrossed`, accessors for OM/metrics/client/call ID, `getBootstrapStateLock`, and `submitSetSnapshotRequests`. Nested `DeletingServiceTaskQueue` wraps every task in a bootstrap read lock.

Control flow and persistence: `shouldRun` requires OM leader readiness unless OM is null for tests. `submitRequest` uses `OzoneManagerRatisUtils.submitRequest` with a stable random `ClientId` and incrementing call ID. `isPreviousPurgeTransactionFlushed` compares deletion metrics' last AOS transaction against disk-flushed transaction info to avoid processing before previous purge metadata is durable. `submitSetSnapshotRequests` builds an OM request of type `SetSnapshotProperty`.

Dependencies and integration: Base class for services that submit purge or snapshot property OM requests. It depends on OM locks, Ratis utils, deletion/perf metrics, transaction info, and bootstrap state handling.

Risks and test signals: Lock wrapping and flush gating prevent races with bootstrap and unflushed purges. Tests should cover suspension waiting for futures, leader gating, bootstrap read lock acquisition for queued tasks, call ID increments, previous-purge flush blocking, and snapshot-property request submission errors.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/AbstractKeyDeletingService.java -->
