# File Research: sources/os/linux/linux/fs/xfs/xfs_fsops.c

Implements filesystem-level operations: growfs, reserve-block tuning, forced shutdown, going-down ioctl behavior, and per-AG/metafile reservations.

Key logic:
- `xfs_resizefs_init_new_ags` initializes new AG headers with delayed-write buffers before the grow transaction is committed; it can also extend the previous last AG.
- `xfs_growfs_data_private` validates target block count, probes new device end, checks realtime geometry, computes AG deltas, rejects unsupported shrink cases, initializes perag structures, initializes new AGs or shrinks the last AG, transactionally updates superblock counters, commits synchronously, updates mount geometry thresholds, reserves AG metadata, and recomputes realtime btree maxlevels.
- `xfs_growfs_log_private` validates requested log size but returns `ENOSYS` for log moving/resizing.
- `xfs_growfs_imaxpct` updates inode allocation percentage transactionally.
- `xfs_growfs_data` and `xfs_growfs_log` enforce `CAP_SYS_ADMIN` and serialize with `m_growlock`.
- `xfs_reserve_blocks` changes reserve-pool targets under `m_sb_lock`, releasing surplus reserve space or trying to fill a larger reserve from free counters without dipping into reserved space.
- `xfs_fs_goingdown` implements user-requested shutdown modes: freeze/thaw default, logflush, and nologflush.
- `xfs_do_force_shutdown` atomically transitions the mount to shutdown, shuts down the log, reports a reason/tag, emits diagnostics, reports to `fserror`, and notifies health monitoring.
- `xfs_fs_reserve_ag_blocks` initializes per-AG metadata reservations and realtime/metafile reservations, forcing shutdown on unexpected reservation errors.
- `xfs_fs_unreserve_ag_blocks` releases metafile and per-AG reservations.

This file is a mount-wide administrative control point and must keep superblock, perag, reservation, and health/shutdown state coherent.
