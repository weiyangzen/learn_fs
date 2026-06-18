<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/ScmBlockDeletingServiceMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/ScmBlockDeletingServiceMetrics.java

## Purpose
Provides Hadoop Metrics2 instrumentation for SCM's background block deleting service. It tracks delete command counts, delete transaction counts, skipped and processed transactions, datanode participation, blocks sent for deletion, live deleted-block-log summaries from `BlockManager`, and per-datanode command outcomes.

## Important APIs, Types, And Functions
`ScmBlockDeletingServiceMetrics` is a singleton `MetricsSource` registered under `SCMBlockDeletingService.class.getSimpleName()`. `create(BlockManager)` registers the metrics instance with `DefaultMetricsSystem`; `unRegister()` clears the singleton and unregisters the source. Increment methods update counters and gauges such as `incrBlockDeletionCommandSent`, `incrBlockDeletionTransactionsOnDatanodes`, `incrBlockDeletionTransactionCompleted`, `incrSkippedTransaction`, `setNumBlockDeletionTransactionDataNodes`, and per-DN `incrDNCommands*` helpers. `getMetrics` snapshots Metrics2 fields and emits extra records from `DeletedBlocksTransactionSummary`. Nested `DatanodeCommandDetails` holds per-datanode sent, success, failure, timeout, and block counts.

## Control Flow
Callers create the singleton during service startup and invoke increment/set methods as delete commands are created, sent, acknowledged, timed out, or completed. Metrics collection calls `getMetrics`, snapshots the annotated mutable counters/gauges, queries `blockManager.getDeletedBlockLog().getTransactionSummary()`, and emits one tagged record for each datanode in `numCommandsDatanode`.

## State And Persistence
State is in-memory metrics state only. The aggregate counters use Metrics2 mutable counters/gauges; per-datanode values live in a `ConcurrentHashMap<DatanodeID, DatanodeCommandDetails>`. The source reads persistent delete-log state indirectly through `BlockManager`, but it does not write SCM metadata.

## Dependencies And Integration Points
Integrates with `SCMBlockDeletingService`, `BlockManager`, the deleted-block log, `HddsProtos.DeletedBlocksTransactionSummary`, Hadoop Metrics2 registry/snapshot APIs, and `DatanodeID`. Observability consumers depend on metric names and tags staying stable.

## Risks And Test Signals
The singleton can retain stale state if `unRegister()` is not called between tests or service restarts. `DatanodeCommandDetails` field increments are not atomic even though the map is concurrent, so concurrent updates to the same datanode can lose increments. `getBNumBlockDeletionCommandFailure` appears to be a typo but may be API-compatible surface. Tests should cover metrics registration/unregistration, aggregate snapshots, per-datanode tagged records, deleted-block-log summary gauges, and concurrent update expectations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/block/ScmBlockDeletingServiceMetrics.java -->
