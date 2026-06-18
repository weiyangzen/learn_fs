# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestOmTableInsightTask.java

Purpose: Broad test suite for `OmTableInsightTask`, which computes Recon global statistics for OM table row counts and size totals. It covers count-only tables and size-bearing tables such as open key/file, deleted key, deleted directory, and multipart info tables.

Important APIs and control flow: `initializeInjector` builds a Recon test injector with SQL DB, Recon OM, container DB, namespace summary manager, global stats manager, `OmTableInsightTask`, and `NSSummaryTaskWithFSO`. Tests call `reprocess` over mocked or real OM tables and `process` over `OMUpdateEventBatch` deltas. Helpers read global stats using `OmTableInsightTask.getTableCountKeyFromTable`, `getUnReplicatedSizeKeyFromTable`, and `getReplicatedSizeKeyFromTable`.

State and persistence behavior: Results persist to Recon SQL `GLOBAL_STATS` through `ReconGlobalStatsManager`. The task maintains in-memory count and size maps initialized from persisted stats. Deleted table counts reflect number of contained `OmKeyInfo` entries, not rows. Deleted-directory size handling depends on namespace summary rows keyed by object ID. Multipart size totals derive from part `KeyInfo` data size and replication factor.

Dependencies and integration points: Integrates OM table definitions, Recon OM metadata manager, `ReconNamespaceSummaryManagerImpl`, `NSSummaryTaskWithFSO`, jOOQ DSL, generated `GlobalStatsTable`, OM helpers, replication configs, and `OMDBUpdateEvent` actions. It is a central consumer of OM update events produced by the update handler.

Risks and test signals: High signal for aggregate correctness across reprocess and incremental paths. Risks include singleton/static task fields in the test class, mock iterator behavior that may hide real table implementation issues, and implicit assumptions about deleted directory path parsing and multipart replication arithmetic.
