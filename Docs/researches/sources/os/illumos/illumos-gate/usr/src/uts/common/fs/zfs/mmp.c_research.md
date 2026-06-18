# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/mmp.c

## Scope

This file implements ZFS Multi-Modifier Protection, which writes periodic MMP heartbeat uberblocks so another host can detect that a multihost pool is active before importing it. The file was read completely.

## APIs And Entry Points

- Lifecycle: `mmp_init()`, `mmp_fini()`, `mmp_thread_start()`, `mmp_thread_stop()`.
- Uberblock state: `mmp_update_uberblock()` copies the last synced uberblock into MMP state and refreshes timestamp/delay tracking.
- Thread signaling: `mmp_signal_all_threads()` wakes active pool MMP threads after tunable changes.
- Internal flow: `mmp_thread()`, `mmp_write_uberblock()`, `mmp_next_leaf()`, `mmp_delay_update()`, `mmp_write_done()`.

## Control Flow

When enabled by the pool’s `multihost` property, `mmp_thread()` periodically selects a writable leaf vdev without an outstanding MMP write and writes a copy of the last synced uberblock into one of the reserved MMP uberblock slots near the end of a randomly chosen label. It updates `ub_mmp_magic`, `ub_mmp_delay`, and `ub_mmp_config`, including sequence, interval, and fail interval values.

`mmp_next_leaf()` rotates through spa leaves under `SCL_STATE` and `mmp_io_lock`, skipping non-writable leaves and leaves with pending MMP writes. `mmp_write_done()` updates delay statistics, clears pending flags on the vdev, exits the spa config lock acquired for the write, and frees the ABD buffer.

The thread recalculates interval and failure thresholds each loop. It writes more aggressively after tunable changes so importers observe new parameters sooner. If multihost is enabled and no MMP write succeeds within the configured fail interval window, the pool is suspended with `ZIO_SUSPEND_MMP`.

## State And Dependencies

Core state lives in `spa->spa_mmp`: thread pointer/exit flag/CV, `mmp_io_lock`, last leaf and leaf-list generation, last synced MMP uberblock copy, sequence counter, delay estimate, last successful write time, skip error, kstat IDs, and root zio.

Dependencies include ABD buffers, vdev label writes, uberblock layout/macros, SPA namespace iteration, spa config locks, vdev writability, leaf lists, `zio_suspend()`, CPR thread support, and tunables `zfs_multihost_interval`, `zfs_multihost_import_intervals`, and `zfs_multihost_fail_intervals`.

## Risks And Invariants

- Import safety depends on visible on-disk heartbeat changes and conservative import wait-time calculation from MMP config/delay fields.
- MMP writes must not overwrite normal txg_sync uberblocks; reserved slots are used.
- Pending writes are per-leaf. A leaf with a stuck MMP write is skipped to avoid piling up writes, but prolonged failures may suspend the pool.
- `mmp_delay` is deliberately not averaged downward too quickly; sudden latency spikes must remain visible to importers.
- `mmp_delay` is set to zero when multihost is off so future imports can skip the activity test.
- `mmp_thread_stop()` waits for the thread and then waits for outstanding MMP zios before clearing the root.

## Summary

`mmp.c` provides the runtime heartbeat half of ZFS multihost protection. It does not prove all possible multi-writer misuse cases, but it gives import code observable disk activity, tunable-derived wait windows, and fail-stop pool suspension when configured heartbeat writes stop succeeding.
