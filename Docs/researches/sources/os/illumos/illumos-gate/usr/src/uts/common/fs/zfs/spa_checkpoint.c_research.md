# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/spa_checkpoint.c

This file implements ZFS storage pool checkpoints: creating a pool-wide rewind point, reporting checkpoint state, and discarding checkpointed space asynchronously.

Key behavior:
- A checkpoint is represented by `DMU_POOL_ZPOOL_CHECKPOINT` in the MOS, containing a checkpointed uberblock, plus active `SPA_FEATURE_POOL_CHECKPOINT` state.
- Checkpointed frees are preserved in top-level vdev checkpoint space maps rather than returned to metaslab allocatable space, preventing reuse of blocks needed for rewind.
- `spa_checkpoint_get_stats()` reports whether the checkpoint exists or is being discarded, plus checkpoint space and timestamp.
- `spa_checkpoint()` opens the pool, waits for the current TXG to sync, then uses `dsl_early_sync_task()` so `spa_checkpoint_sync()` runs before ordinary frees in the next TXG.
- `spa_checkpoint_check()` rejects unsupported pools, too-large vdev space map addressing, active vdev removal, an existing checkpoint, or an in-progress discard.
- `spa_checkpoint_sync()` stores `spa_ubsync` as the checkpoint uberblock, sets `spa_checkpoint_txg`, records timestamp, adds the MOS ZAP entry, increments the feature refcount, and logs history.
- `spa_checkpoint_discard()` starts discard with an early synctask that removes the MOS checkpoint entry, clears `spa_checkpoint_txg`, wakes the discard thread, and logs the start.
- `spa_checkpoint_discard_thread()` walks top-level vdev checkpoint space maps, prefetches bounded chunks, and schedules syncing work to transfer checkpointed frees into metaslab freeing trees.
- `spa_checkpoint_discard_thread_sync()` destroys checkpoint space-map entries incrementally, updates `sci_dspace` and per-vdev checkpoint accounting, and frees/removes empty checkpoint space maps.
- `spa_checkpoint_discard_complete_sync()` clears the timestamp, decrements the feature refcount, wakes waiters, and logs completion after all vdev checkpoint maps are gone.

Important invariants:
- Checkpoint create and discard both use early synctasks to avoid races with frees entering checkpoint data structures.
- Discard iteration works backward through space maps and is bounded by `zfs_spa_discard_memory_limit`.
- Checkpoint accounting is verified in debug builds by comparing per-vdev checkpoint space, checkpoint space maps, and `spa_checkpoint_info.sci_dspace`.
