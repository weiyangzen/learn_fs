## sources/user-network-fs/gcsfuse/internal/gcsx/garbage_collect.go

Purpose: deletes stale temporary GCS objects created by append/compose flows under a configured prefix.

Important APIs/functions: `garbageCollectOnce(ctx, tmpObjectPrefix, bucket)` and `garbageCollect(ctx, tmpObjectPrefix, bucket)`.

Control flow: `garbageCollectOnce` creates an `errgroup` pipeline: list all objects with the prefix into a channel, filter objects older than a 30-minute staleness threshold into stale names, then delete each stale object with generation `0`. It increments `objectsDeleted` atomically. `garbageCollect` wakes every 10 minutes until context cancellation and logs success or failure with elapsed time and partial delete count.

State and persistence behavior: no local state. Remote persistent action is deleting latest generations of stale temp objects. Time-based filtering is computed once per run, so objects near threshold are consistently judged for that pass.

Dependencies/integration: uses `storageutil.ListPrefix`, GCS delete requests, `errgroup`, atomic counters, context cancellation, and internal logger. It is intended as cleanup for temporary junk that `composeObjectCreator` may leave behind.

Risks/test signals: delete generation `0` targets latest generation and may delete a newer temp object with the same name if names collide, though names are random. A single delete/list error aborts the run. No test file for this item was listed, so behavior is inferred from implementation.
