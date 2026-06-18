<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/live_restore/live_restore_server.c -->
# sources/storage-engines/wiredtiger/src/live_restore/live_restore_server.c

## Purpose
Implements the background migration server that drains live-restore work items, opens data handles safely through cursors, copies holes from source to destination, and performs post-migration cleanup/checkpointing.

## Important APIs, Types, and Functions
Public entry points are `__wt_live_restore_server_create` and `__wt_live_restore_server_destroy`. Internal helpers include `__live_restore_init_work_queue`, `__insert_queue_item`, `__live_restore_worker_run`, `__live_restore_worker_stop`, `__live_restore_clean_up`, `__live_restore_work_queue_drain`, and `__live_restore_free_work_item`. The worker calls `__wti_live_restore_fs_restore_file` on the block manager's live-restore file handle.

## Control Flow
Server creation returns immediately if live restore is disabled. If migration is already complete, it opens an internal session and runs cleanup without starting workers. Otherwise, if `threads_max` is nonzero, it allocates the server, initializes the queue lock and work queue, sets `threads_working`, starts progress timers, and creates a fixed-size thread group. The queue is built by scanning metadata for `file:` URIs and optionally adding `file:WiredTiger.wt` unless partial-backup restore will rebuild metadata. Worker runs wait for `WT_CONN_READY`, pop one URI, report periodic progress, open a cursor to prevent exclusive schema access, restore the underlying file, and free the work item. `ENOENT` drops the item; `EBUSY` requeues it and may sleep if workers exceed remaining items. When the last worker stops and the queue is empty, cleanup runs.

## State and Persistence Behavior
Queue counters update `live_restore_work_remaining`, `work_count`, and `work_items_remaining`. Cleanup forces a checkpoint before leaving background migration so empty bitmaps are durable, advances the persisted live-restore state to `CLEAN_UP`, removes stop files, optionally delays for timing-stress sweep cleanup, forces another checkpoint to remove live-restore metadata, then persists `COMPLETE`. Destroy marks `shutting_down`, destroys the thread group if present, drains queued work, and frees server memory; unfinished work is recoverable because file bitmap/state metadata is persisted by checkpoints.

## Dependencies and Integration Points
Uses WiredTiger thread groups, metadata cursors, internal sessions, checkpoints, btree/block-manager internals, live-restore FS restore routines, stats, verbose progress logging, connection flags, and private state helpers. Connection open invokes create; connection close/error paths invoke destroy.

## Risks and Edge Cases
Cleanup is triggered from worker-stop while holding the queue lock, so it must not require queue operations that would self-deadlock. Workers must wait for `WT_CONN_READY` to avoid racing connection flag setup and checkpoint side effects. `EBUSY` requeue behavior protects concurrent schema/bulk operations but can delay completion. The direct block-manager access is marked as a FIXME and is fragile if the block-manager structure changes or multi-handle btrees become relevant. If `threads_max=0`, no background migration occurs until a later run with workers or application reads/writes force data movement.

## Test Signals
End-to-end live-restore tests should verify work queue population, thread startup/shutdown, EBUSY retry paths, restart during migration, cleanup checkpoints, stop-file cleanup, and final `WT_LIVE_RESTORE_COMPLETE` stats. Progress stats and logs provide operational signals: remaining work count, source reads, bytes copied, and periodic progress messages.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/live_restore/live_restore_server.c -->
