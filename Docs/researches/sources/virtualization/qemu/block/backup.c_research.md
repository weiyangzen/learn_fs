# File Research: sources/virtualization/qemu/block/backup.c

This file implements QEMU block backup jobs using copy-before-write filtering and the shared `block-copy` engine.

Key structures:
- `BackupBlockJob` embeds `BlockJob` and stores the copy-before-write node, source and target BDS pointers, optional sync bitmap, sync/bitmap modes, source/target error policies, image length, cluster size, performance settings, `BlockCopyState`, and state for a background block-copy call.

Major flows:
- `backup_job_create()` validates source/target presence and size, rejects source equal to target, checks compression support, operation blockers, worker/chunk constraints, and optional dirty-bitmap writability.
- It creates a successor dirty bitmap when incremental bitmap synchronization is requested.
- It appends a copy-before-write filter with `bdrv_cbw_append()`, obtains a `BlockCopyState`, creates the block job on the CBW node, configures block-copy options/progress/speed, and adds the target as a job BDS.
- `backup_run()` initializes the copy bitmap, handles `sync=top` by scanning/resetting unallocated regions, then either waits for cancellation in `sync=none` mode or runs `backup_loop()`.
- `backup_loop()` repeatedly launches `block_copy_async()` over the full aligned job length, waits/yields for completion or cancellation, and handles read/write errors according to backup error policies.
- `backup_pause()` cancels an active block-copy call and waits for it to finish.
- `backup_cancel()` cancels target in-flight requests.
- `backup_commit()` and `backup_abort()` reconcile the sync bitmap differently depending on success/failure and `BitmapSyncMode`.

Bitmap semantics:
- `backup_cleanup_sync_bitmap()` either abdicates the successor into the parent bitmap or reclaims it.
- With `BITMAP_SYNC_MODE_ALWAYS`, failure still syncs and then merges bits that were not copied back from the block-copy dirty bitmap.
- `backup_do_checkpoint()` only supports `sync=none` and marks the entire block-copy bitmap dirty for future CBW-triggered copying.

Concurrency and job model:
- Backup work is coroutine-driven through the job framework.
- Background copy is represented by `BlockCopyCallState`; callbacks wake the job coroutine or re-enter the job.
- Cancellation and pause rely on `block_copy_call_cancel()` plus explicit coroutine yield/wake coordination.

Filesystem/block relevance:
- This is a central virtual block snapshot/backup mechanism.
- It combines dirty bitmaps, copy-before-write filters, block graph permissions, and target writes to preserve point-in-time source content.

Potential pitfalls:
- Source and target lengths must match exactly.
- `max_chunk` must be zero or at least the copy cluster size.
- `sync=none` jobs do not proactively copy; they rely on CBW write interception until cancellation/completion semantics decide lifecycle.
