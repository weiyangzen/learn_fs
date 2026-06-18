# sources/sync-backup/restic/internal/archiver/tree_saver.go

Purpose: Concurrently serializes directory nodes into restic tree blobs after child file/tree futures have completed.

Important APIs and types: `treeSaver` owns a `BlobSaverAsync`, error handler, and job channel. `newTreeSaver`, `TriggerShutdown`, `Save`, `saveTreeJob`, `save`, and `worker` implement the queue and worker lifecycle.

Control flow and state: `Save` enqueues a tree job and returns a future. `save` consumes child `futureNode` values in order, applies error filtering through `errFn`, skips excluded/nil nodes, adds nodes to `data.NewTreeJSONBuilder`, tolerates duplicate identical adjacent nodes by warning, finalizes JSON, uploads it as a `TreeBlob`, updates `ItemStats`, and sets `node.Subtree` to the new tree ID. Workers return fatal errors through the errgroup.

Persistence and dependencies: Tree blobs are persisted through `SaveBlobAsync`; state is otherwise per-job. Dependencies include `data`, `restic`, `errgroup`, context cancellation, and `ErrorFunc`.

Integration points: Directory saving in the main archiver schedules `treeSaver` jobs after file and child directory futures. Its stats are merged into snapshot summaries.

Risks and test signals: Risks include deadlocks waiting on futures, missing context cancellation, duplicate-name ordering errors, ignored errors dropping nodes, and worker termination on upload failures. `tree_saver_test.go` validates success, injected child errors, and duplicate handling.
