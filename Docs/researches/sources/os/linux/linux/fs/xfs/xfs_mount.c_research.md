# File Research: sources/os/linux/linux/fs/xfs/xfs_mount.c

## Purpose

`xfs_mount.c` implements core XFS mount and unmount lifecycle logic, superblock reading, UUID uniqueness, geometry setup, free-space accounting, log feature flag updates, reserve-pool handling, and delayed allocation accounting.

## Main Responsibilities

- Maintain a global mounted-filesystem UUID table.
- Read and validate the primary superblock.
- Initialize mount geometry, feature state, directory/attribute geometry, realtime metadata, per-AG and rtgroup state, quota state, log state, and work queues.
- Perform mount-time recovery sequencing in cooperation with the log code.
- Tear down mounted filesystems cleanly during unmount or failed mount.
- Manage free block and realtime extent counters with reserve pools.
- Validate and configure stripe alignment, allocation size, low-space thresholds, and atomic write limits.
- Add and clear log incompat feature bits safely.
- Track delayed allocation blocks and realtime extents.

## Key Mount Flow

`xfs_mountfs` is the main mount function. It:

1. Initializes common superblock-derived mount state.
2. Corrects legacy mismatched `features2` state if necessary.
3. Ensures v2 inode/link-count feature state.
4. Validates and applies stripe alignment options.
5. Computes btree and inode geometry.
6. Initializes sysfs, scrub stats, error tags, and UUID registration.
7. Validates sparse inode alignment and device sizes.
8. Initializes realtime mount fields and directory/attribute geometry.
9. Initializes transaction reservations, per-AG state, and rtgroups.
10. Registers inodegc shrinker.
11. Mounts the log and performs the first recovery phase.
12. Starts inodegc and blockgc.
13. Loads metadata directory, root inode, and realtime inodes.
14. Checks summary counters.
15. Syncs superblock updates if needed and writable.
16. Initializes quota management.
17. Finishes log recovery after root/realtime metadata is available.
18. Cleans log for read-only recovered mounts.
19. Mounts zoned state if enabled.
20. Reserves free-space pools and AG metadata space.
21. Computes atomic write unit maxima.

The error path unwinds each stage in reverse order, including inode release, quota cleanup, inodegc flushing, log cancellation, buftarg draining, group freeing, UUID removal, sysfs cleanup, and scrub stats unregistering.

## Key Unmount Flow

`xfs_unmountfs`:

- Flushes inodegc.
- Stops blockgc and zone gc.
- Releases AG reservations and quota state.
- Unmounts zoned, realtime, root, and metadata directory inodes.
- Flushes inodes and AIL through `xfs_unmount_flush_inodes`.
- Unmounts quota internals.
- Releases reserved block pools.
- Checks free inode counters.
- Marks log incompat bits clearable and unmounts the log.
- Frees DA geometry, UUID table entry, shrinker, rtgroups, per-AG state, error tags, scrub stats, and sysfs state.

## Important Functions

- `xfs_uuid_mount` / `xfs_uuid_unmount`: enforce unique non-null UUIDs unless `nouuid` is set.
- `xfs_readsb`: reads the superblock first with device sector size, then rereads with filesystem sector size and verifiers.
- `xfs_validate_new_dalign`: validates mount-option stripe unit/width and converts them to fsblocks.
- `xfs_update_alignment`: applies stripe alignment changes or reads existing superblock alignment.
- `xfs_set_low_space_thresholds`: computes 1%-5% free-space thresholds for speculative preallocation.
- `xfs_check_sizes`: verifies readable last sector of data and external log devices.
- `xfs_mount_reset_sbqflags`: clears quota flags in-core and on disk when needed.
- `xfs_default_resblks`: computes default reserve pools.
- `xfs_check_summary_counts`: validates or recomputes summary counters after log recovery.
- `xfs_unmount_flush_inodes`: forces log, waits for busy extents/discards, stops inodegc, pushes AIL, reclaims inodes, and unmounts health state.
- `xfs_set_max_atomic_write_opt`: validates user-requested max atomic write size and computes reservation support.
- `xfs_fs_writable`: checks freeze level, shutdown, and readonly state.
- `xfs_add_freecounter` / `xfs_dec_freecounter`: update free counters and reserve pools.
- `xfs_add_incompat_log_feature`: safely writes log incompat bits to the primary superblock before later log items require them.
- `xfs_clear_incompat_log_features`: clears log incompat flags when safe.
- `xfs_mod_delalloc`: updates delayed allocation counters for data or realtime inodes.

## Free-Space Accounting

The file uses percpu counters for free blocks, free realtime extents, available realtime extents, allocated/free inode counts, and delayed allocation counts. `xfs_dec_freecounter` uses large batches under normal conditions but switches to accurate accounting near ENOSPC. Reserved pools can be consumed only by callers passing `rsvd`.

## Atomic Write Handling

Atomic write maximums are constrained by:

- kernel maximum write size,
- reflink CoW completion limits,
- group size and group alignment,
- hardware atomic-write support,
- filesystem block alignment,
- transaction reservation feasibility.

The computed per-group maxima are stored in `m_groups[type].awu_max`.

## Error Handling

Mount initialization has extensive staged unwind labels. Metadata corruption uses `XFS_IS_CORRUPT` where applicable. Read-only devices reject operations requiring write access, such as recovery. Mount can continue without reserve pools in some ENOSPC cases but fails on structural or recovery errors.
