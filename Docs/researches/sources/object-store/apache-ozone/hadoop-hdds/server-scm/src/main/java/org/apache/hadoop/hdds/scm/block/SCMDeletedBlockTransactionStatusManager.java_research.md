# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/SCMDeletedBlockTransactionStatusManager.java

Purpose: Manages in-memory deleted-block transaction and delete-command status to suppress duplicate sends, process ACKs, remove fully committed transactions, and maintain pending-deletion summary counters.

Important APIs and types: Owns commit map, retry-count map, transaction-size map, `DeletedBlockLogStateManager`, `ContainerManager`, metrics, and inner `SCMDeleteBlocksCommandStatusManager` with `TO_BE_SENT` and `SENT` states.

Control flow: Command records start `TO_BE_SENT`, become `SENT` on dispatch, and are removed on executed/failed reports or timeout. `recordTransactionCreated` initializes command and commit-map entries. `isDuplication` checks committed and in-processing states. `commitTransactions` records successful datanode ACKs and removes a transaction only once all current replica datanodes have committed and required node count is met. Add/remove methods persist through the state manager and update summary counters when storage-space-distribution is finalized.

State and persistence behavior: Command status, retry counts, commit map, and size map are in memory and cleared on leadership changes. Aggregate summary is loaded from and written to the stateful config table.

Dependencies and integration points: Called by `DeletedBlockLogImpl` during scans, command creation, ACK/status handling, datanode death, leadership change, and reinitialization.

Risks: Maps can grow if datanodes do not respond; timeout cleanup and service thresholds mitigate this. Async retry count updates are diagnostic and eventually consistent. Summary counters may drift if size metadata is missing.

Test signals: Cover state transitions, duplicate detection, timeout cleanup, datanode death, leadership reset, failed/successful ACKs, all-replica commit criteria, summary persistence, and reinitialize loading.
