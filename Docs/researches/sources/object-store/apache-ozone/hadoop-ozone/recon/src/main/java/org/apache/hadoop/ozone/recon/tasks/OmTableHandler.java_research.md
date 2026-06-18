# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/OmTableHandler.java

Purpose: `OmTableHandler` is the strategy interface used by `OmTableInsightTask` for OM tables that need more than simple record counting. Its implementations calculate object counts plus unreplicated and replicated byte totals for size-related tables.

Important APIs and types: `handlePutEvent`, `handleDeleteEvent`, and `handleUpdateEvent` mutate supplied maps for object counts, logical size, and replicated size. `getTableSizeAndCount` performs full-table scanning during reprocess and returns a `Triple<count, unreplicatedSize, replicatedSize>`. Default key helpers create global stats keys such as `<table>Count`, `<table>ReplicatedDataSize`, and `<table>UnReplicatedDataSize`.

Control flow and integration: `OmTableInsightTask` registers handlers for open key, open file, deleted, and multipart tables. Incremental OMDB events are routed to the handler based on action. Full reprocess calls `getTableSizeAndCount`.

State and persistence: handlers operate on caller-provided maps and do not store durable state. Persistence happens later when `OmTableInsightTask.writeDataToDB` writes global stats via `ReconGlobalStatsManager`.

Dependencies: `OMDBUpdateEvent`, `OMMetadataManager`, Apache Commons `Triple`.

Risks and test signals: implementors must handle null values and old values consistently, must avoid negative counters on deletes, and must return values compatible with global stat key naming. Unit tests should include PUT, DELETE, UPDATE, null payloads, and full table scans for each handler implementation.
