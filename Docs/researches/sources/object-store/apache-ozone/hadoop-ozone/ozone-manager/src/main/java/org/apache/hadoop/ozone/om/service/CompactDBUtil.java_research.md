<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/CompactDBUtil.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/CompactDBUtil.java

Purpose: Utility for manual full compaction of OM RocksDB column families.

Important APIs/types/functions: Final utility class with private constructor. `compactTable(OMMetadataManager, String)` performs synchronous compaction. `compactTableAsync` wraps it in a `CompletableFuture`.

Control flow and persistence: `compactTable` creates `ManagedCompactRangeOptions`, forces bottommost-level compaction, requests exclusive manual compaction, obtains the `RocksDatabase` from `RDBStore`, resolves the column family by table name, throws `IOException` if missing, and calls `compactRange`. Async mode logs and rethrows failures through `CompletionException`.

Dependencies and integration: Used by `CompactionService` and on-demand compaction paths. Depends on OM metadata store being an `RDBStore`.

Risks and test signals: Manual compaction can be expensive and table-name sensitive. Tests should cover valid table compaction, missing column family error, async failure propagation, and option settings for forced bottommost compaction.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/CompactDBUtil.java -->
