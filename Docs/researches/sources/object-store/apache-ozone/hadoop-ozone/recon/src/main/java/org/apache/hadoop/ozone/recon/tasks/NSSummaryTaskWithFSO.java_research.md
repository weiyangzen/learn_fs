# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/NSSummaryTaskWithFSO.java

Purpose: Namespace summary subtask for File System Optimized tables.

Important APIs: `getTaskTables`, `processWithFSO`, `reprocessWithFSO`, and private handlers for file table, directory table, deleted directory table, and parallel reprocess phases.

Control flow and persistence: incremental processing starts at a supplied seek position, filters to `FILE_TABLE`, `DIRECTORY_TABLE`, and `DELETED_DIR_TABLE`, applies file or directory handlers, collects hard-deleted directory object IDs, and flushes updates plus deletes when the map reaches threshold. Reprocess runs in two phases: directory table first, then file table, each parallelized with worker-local maps and `NSSummaryAsyncFlusher`. Directory skeletons are persisted before file deltas propagate.

Dependencies and integration: extends `NSSummaryTaskDbEventHandler`; uses `ParallelTableIteratorOperation`, `StringCodec`, OM file and directory tables, and `ReconNamespaceSummaryManager`.

Risks: `eventCounter` counts all events after seek, not only processed task-table events, so seek semantics must match the shared event stream. The objectIds-to-delete list is reused across flushes intentionally, which repeats delete attempts. Reprocess correctness depends on directory phase completing and closing its flusher before file phase starts.

Test signals: cover file PUT/DELETE/UPDATE, directory PUT/DELETE/UPDATE, deleted-dir hard delete, seek-position continuation, two-phase reprocess, and async flusher failure during either phase.
