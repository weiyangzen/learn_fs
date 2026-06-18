# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_trim.c

## Role
Implements manual TRIM (`zpool trim`) and automatic TRIM (`autotrim=on`) for ZFS vdevs. Manual trim is per leaf vdev and persists progress/options to leaf ZAP state; autotrim is per top-level vdev and continuously processes recently freed metaslab ranges without persistent progress.

## Tunables And Data Model
- `zfs_trim_extent_bytes_max`: max TRIM I/O chunk size, default 128 MiB.
- `zfs_trim_extent_bytes_min`: minimum range worth trimming, default 32 KiB.
- `zfs_trim_metaslab_skip`: declared skip-uninitialized-metaslabs setting; the active manual path uses the persisted `vdev_trim_partial` option.
- `zfs_trim_queue_limit`: max queued trim I/Os per leaf vdev across manual and auto trim.
- `zfs_trim_txg_batch`: minimum txg spacing for autotrim revisiting a metaslab.
- `trim_args_t` carries the target leaf vdev, disabled metaslab, range tree, trim type, limits, flags, start time, and bytes done.

## Manual TRIM Flow
- `vdev_trim()` requires a concrete leaf vdev with no existing manual trim thread, persists state via `vdev_trim_change_state()`, then starts `vdev_trim_thread()`.
- `vdev_trim_thread()` waits for requested ZAP options to sync, loads trim state/progress, configures secure/partial/rate options, iterates top-level metaslabs sequentially, disables each metaslab, loads free ranges from `ms_allocatable`, converts ranges through `vdev_xlate()`, issues trim I/O, re-enables the metaslab, and completes state if not stopped.
- `vdev_trim_load()` reads `VDEV_LEAF_ZAP_TRIM_*` fields and calculates progress.
- `vdev_trim_calculate_progress()` estimates done/total bytes by comparing `vdev_trim_last_offset` with each metaslab's physical range and, for the current metaslab, walking loaded allocatable ranges.
- `vdev_trim_stop()`, `vdev_trim_stop_all()`, `vdev_trim_stop_wait()`, and `vdev_trim_restart()` implement suspend/cancel/stop/restart around persisted ZAP state.

## Automatic TRIM Flow
- `vdev_autotrim()` starts one thread per writable, non-removing top-level vdev.
- `vdev_autotrim_thread()` loops until autotrim is disabled, the vdev is no longer writable, or removal/exit is requested.
- Metaslabs are grouped by `zfs_trim_txg_batch`; each loop picks a strided group so revisits are txg-spaced and spatially distributed.
- For each metaslab with recent frees in `ms_trim`, autotrim disables the metaslab, swaps `ms_trim` into a private tree, builds per-leaf trim trees, skips detached/unwritable/non-trim/manual-trimming children, and issues best-effort trim I/O.
- If autotrim is turned off, unprocessed `ms_trim` ranges are vacated to reclaim memory.
- `vdev_autotrim_stop_wait()`, `vdev_autotrim_stop_all()`, and `vdev_autotrim_restart()` control lifecycle.

## I/O Submission And Safety
- `vdev_trim_range()` enforces manual rate limiting, queue depth, txg creation, config/state locking, stop checks, progress offset persistence scheduling, and `zio_trim()` submission.
- `vdev_trim_ranges()` splits large ranges into legal physical chunks and waits for manual trim inflight I/O to drain before returning.
- Both manual and autotrim use `spa_config_enter(SCL_STATE_ALL)` before submission; callbacks release it.
- `vdev_trim_cb()` handles manual completion, records errors, rolls back last offset on ENXIO/unwritable failures, updates bytes done, decrements inflight, and wakes waiters.
- `vdev_autotrim_cb()` records best-effort errors/success bytes and never reissues failed I/O.

## Persistent State
- `vdev_trim_zap_update_sync()` writes manual trim state to the leaf ZAP: last offset, action time, rate, partial, secure, and trim state.
- `vdev_trim_change_state()` handles state transitions, sentinel resets after completed/canceled trims, requested option persistence, event notification, and history logging.

## Important Details
- While a metaslab is disabled for trim it is not eligible for allocation; the code waits for trim I/O before enabling the metaslab to avoid lower-priority trim racing later writes to the same ranges.
- Secure manual trim lowers the minimum trim range to `SPA_MINBLOCKSIZE`, treating skipped small ranges as unacceptable.
- Manual trim progress is physical-offset based, which matters for raidz translation and resume.
- Autotrim intentionally skips devices with hot spares/replacements or manual trim activity to avoid stressing devices and to yield to explicit operator action.
