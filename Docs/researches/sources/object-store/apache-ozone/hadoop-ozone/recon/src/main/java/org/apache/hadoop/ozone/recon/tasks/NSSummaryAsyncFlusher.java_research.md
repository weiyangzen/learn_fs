# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/NSSummaryAsyncFlusher.java

Purpose: Background queue-based flusher for namespace summary reprocess workers. It merges worker-local `NSSummary` deltas with persisted summaries and propagates file deltas up ancestor chains before writing batches.

Important APIs: static `create`, `submitForFlush`, `checkForFailures`, `close`, and private `flushLoop`, `flushWithPropagation`, `propagateDeltaToAncestors`, `writeToDb`.

Control flow and persistence: workers submit maps to a bounded `LinkedBlockingQueue`, giving natural backpressure. The daemon flusher polls until stopped and queue-drained. Each batch is merged with current DB state, child-dir and metadata fields are repaired, numeric file deltas are applied, and file counts/sizes are propagated through parents found in merged map or DB. Writes use `RDBBatchOperation`.

Dependencies and integration: used by `NSSummaryTaskWithFSO` and `NSSummaryTaskWithOBS` during reprocess. It writes through `ReconNamespaceSummaryManager`.

Risks: `close` sets STOPPING and then `join`s without interrupt or timeout; if the background thread is blocked in `poll` it should wake, but a stuck DB write can hang close. Failure state rejects new submissions and may leave queued batches unprocessed. Propagation stops if an ancestor is not yet present in DB, so task phase ordering is critical.

Test signals: cover queue backpressure, DB write failure propagation, close drains all submitted batches, ancestor propagation, metadata repair, and missing-ancestor behavior.
