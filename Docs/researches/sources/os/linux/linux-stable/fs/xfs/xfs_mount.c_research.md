# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_mount.c

## Purpose
Implements XFS mount and unmount orchestration, superblock reading, UUID uniqueness tracking, filesystem geometry setup, log recovery sequencing, free-space reservations, summary counter handling, atomic-write limits, and mount-time teardown paths.

## Main APIs
- `xfs_readsb` reads and verifies the primary superblock, first using device sector size and then the filesystem sector size.
- `xfs_mountfs` performs full mount setup from superblock normalization through log recovery, quota setup, root/realtime inode loading, reservations, and background worker startup.
- `xfs_unmountfs` flushes inodegc/blockgc/quota/log state, writes a clean unmount, releases in-core structures, and unregisters mount resources.
- `xfs_fs_writable` checks freeze, shutdown, and readonly state.
- `xfs_dec_freecounter` and `xfs_add_freecounter` maintain per-cpu free block/realtime counters plus reserved pools.
- `xfs_add_incompat_log_feature` and `xfs_clear_incompat_log_features` manage primary-superblock log-incompat bits.
- `xfs_set_max_atomic_write_opt` validates and stores the mount atomic-write limit.

## Mount Flow
The mount path computes btree heights and inode geometry, validates or imports stripe alignment, initializes sysfs/debug/error infrastructure, enforces UUID uniqueness, checks data/log device sizes, initializes realtime and per-AG/rtgroup state, starts log mount and first-stage recovery, loads metadata/root/realtime inodes, validates summary counts, initializes quotas, finishes log recovery, and reserves critical metadata/free-space pools.

## Counter and Reservation Behavior
The file sets low-space thresholds, recomputes summary counters after unclean mounts or sick counters, restores realtime free extent counts when needed, reserves default emergency pools, and prevents regular allocations from consuming blocks needed by allocation btrees or privileged metadata transactions.

## Unmount and Error Paths
Unmount forces the log, drains busy extents/discards, stops inodegc/blockgc/zonegc, pushes the AIL, reclaims inodes, unmounts quotas/realtime structures, clears UUID registration, and tears down per-AG/rtgroup/sysfs/error-tag state. Partial mount failures follow a carefully ordered cleanup path to cancel log recovery, flush reclaim, drain buffer targets, and release initialized subsystems.

## Feature Handling
The file corrects old `features2` alignment issues, promotes v2 inode support, handles logged xattr opstate, validates unknown dirty-log features before recovery, computes group-level atomic write maxima from kernel limits, reflink capacity, and hardware constraints, and supports zoned realtime mount/GC setup.
