# File Research: sources/os/linux/linux/fs/xfs/xfs_mount.h

## Purpose

`xfs_mount.h` defines the central `struct xfs_mount`, mount feature flags, operational state bits, free counter helpers, shutdown flags, mount lifecycle prototypes, and mount-level utility interfaces.

## Main Structures

- `struct xfs_error_cfg`: sysfs-backed retry configuration for metadata error handling.
- `struct xfs_inodegc`: per-cpu deferred inode inactivation list and work state.
- `struct xfs_groups`: geometry container for allocation groups and realtime groups.
- `struct xfs_freecounter`: percpu free counter plus reserve pool accounting.
- `struct xfs_mount`: the main in-core filesystem mount object.

## `struct xfs_mount` Contents

The mount object stores:

- In-core superblock and Linux superblock pointer.
- AIL, log, primary and realtime superblock buffers.
- Root, metadata directory, realtime directory, quota, device target, and filestream references.
- Workqueues for buffer, unwritten extent, reclaim, sync, blockgc, and inodegc work.
- Precomputed block, inode, btree, realtime, directory, transaction, and allocation geometry.
- Feature and opstate bitmasks.
- Health, sickness, checked-state, scrub, sysfs, debugfs, errortag, and stats state.
- Per-cpu counters and reserve pools.
- Data and realtime group geometry.
- Inodegc shrinker, delayed work, growfs generation/lock, hook lists, health monitor pointer, and UUID table index.

The layout intentionally places read-mostly fields before frequently modified counters and locks.

## Feature Flags

`XFS_FEAT_*` bits describe active filesystem and mount features, including attrs, quotas, CRCs, rmapbt, reflink, sparse inodes, metadir, zoned realtime, DAX policy, filestreams, no-recovery, and nouuid.

The header generates feature helpers with macros such as:

- `xfs_has_reflink`
- `xfs_has_rmapbt`
- `xfs_has_metadir`
- `xfs_has_zoned`
- `xfs_has_norecovery`
- `xfs_has_nouuid`

Some features also have `xfs_add_*` helpers that update both in-core features and superblock version state.

## Operational State

`XFS_OPSTATE_*` bits represent dynamic mount state:

- unmounting,
- clean,
- shutdown,
- inode32,
- readonly,
- inodegc/blockgc enabled,
- one-time experimental warnings,
- quotacheck/resuming quotaon,
- log incompat cleanup state,
- logged xattrs enabled,
- zonegc running.

The header generates `xfs_is_*`, `xfs_set_*`, and `xfs_clear_*` helpers for these bits.

## Shutdown Flags

Defines `SHUTDOWN_META_IO_ERROR`, `SHUTDOWN_LOG_IO_ERROR`, `SHUTDOWN_FORCE_UMOUNT`, `SHUTDOWN_CORRUPT_INCORE`, `SHUTDOWN_CORRUPT_ONDISK`, and `SHUTDOWN_DEVICE_REMOVED`, plus string mappings for tracing/reporting.

## Free Counter Helpers

The header provides inline wrappers for:

- summing, estimating, comparing, and setting free counters,
- decrementing/adding data free blocks,
- decrementing/adding realtime extents,
- accounting delayed allocation blocks.

The main implementations live in `xfs_mount.c`.

## Public Interfaces

Important declarations include:

- `xfs_mountfs`, `xfs_unmountfs`
- `xfs_readsb`, `xfs_freesb`
- `xfs_fs_writable`
- `xfs_sb_validate_fsb_count`
- `xfs_default_resblks`
- `xfs_dev_is_read_only`
- `xfs_set_low_space_thresholds`
- `xfs_zero_extent`
- `xfs_error_get_cfg`
- `xfs_force_summary_recalc`
- `xfs_add_incompat_log_feature`
- `xfs_clear_incompat_log_features`
- `xfs_mod_delalloc`
- `xfs_set_max_atomic_write_opt`
- `xfs_group_type_buftarg`

## Notes

This header is a major cross-subsystem contract. Many XFS subsystems depend on it for feature predicates, mount state transitions, free-space accounting, and access to core mount geometry.
