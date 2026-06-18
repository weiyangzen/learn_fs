# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/OmTableInsightTask.java

Purpose: `OmTableInsightTask` is a `ReconOmTask` that maintains global Recon stats for every OM metadata table, including table object counts and size totals for selected key-related tables. It supports both full reprocess from OM RocksDB and incremental update from OM delta events.

Important APIs and types: `init()` loads table names and initializes count and size maps from current global stats. `reprocess(OMMetadataManager)` scans all OM tables and writes reconstructed stats. `process(OMUpdateEventBatch, Map)` applies PUT, DELETE, and UPDATE deltas. `getStagedTask` creates a task bound to a staged Recon DB for controller reinitialization. Helpers include `initializeCountMap`, `initializeSizeMap`, key-name builders, and test setters.

Control flow: full reprocess iterates over `tables`. Handler tables call `OmTableHandler.getTableSizeAndCount`; non-string key tables use sequential byte-key iteration; string-key count-only tables use `ParallelTableIteratorOperation`. Incremental processing iterates the event batch, skips untracked tables, dispatches by action, updates in-memory maps, then batch-writes global stats. `writeDataToDB` opens an atomic RocksDB batch operation, stores `GlobalStatsValue` entries, and commits.

State and persistence: mutable maps cache stats across processing. Durable state is Recon global stats stored through `ReconGlobalStatsManager`; staged reprocess writes to staged DB before the controller swaps providers.

Dependencies: OM DB definitions, Recon metadata managers, table handlers, RocksDB batch APIs, `ParallelTableIteratorOperation`, Guice, and `Time`.

Risks and test signals: `processTableInParallel` puts the same count key twice, harmless but suspicious. Map state is reused, so tests should cover init ordering, delta after reprocess, negative-bound delete behavior, handler size arithmetic, write failures that only log, non-string table fallback, and staged DB manager binding.
