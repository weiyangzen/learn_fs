# File Research: sources/os/linux/linux/fs/btrfs/super.c

## Scope And Role

`super.c` implements Btrfs integration with the Linux VFS superblock and filesystem-type APIs. It covers mount option parsing, fs_context lifecycle, initial mount, subvolume mounting, remount/reconfigure, sync, statfs, freeze/unfreeze, device control ioctls, superblock operations, shrinker hooks, block-device removal handling, module initialization, and module teardown.

It is the primary Btrfs entry point from the kernel VFS and module loader.

## Filesystem Context And Mount Options

`struct btrfs_fs_context` stores parsed mount state:

- `subvol_name`
- `subvol_objectid`
- `max_inline`
- `commit_interval`
- `metadata_ratio`
- `thread_pool_size`
- `mount_opt`
- `compress_type`
- `compress_level`
- `refs`

The option tables define accepted parameters for ACLs, compression, subvolumes, devices, discard, fatal error behavior, free-space cache, SSD options, rescue modes, ENOSPC debug, and debug-only fragmentation/reference verification options.

`btrfs_parse_param()` uses the new mount API parser and maps parsed options into `btrfs_fs_context`. It handles interactions such as:

- Compression clears `NODATACOW` and `NODATASUM`.
- `nodatacow` disables compression and data checksums.
- `ssd_spread` implies `ssd`.
- `discard=sync` and `discard=async` are mutually exclusive.
- `space_cache=v1` and `space_cache=v2` select old cache or free-space tree.
- Rescue options are grouped under `rescue=`.
- Deprecated `usebackuproot` and compatibility `norecovery` map to rescue-style flags.

`btrfs_parse_compress()` parses zlib/lzo/zstd compression and optional levels, including force-compress handling.

## Option Validation And Defaults

`btrfs_check_options()` rejects rescue options that require read-only mounts, prevents disabling free-space-tree when required by on-disk features, delegates zoned mount-option validation, and warns about deprecated space cache v1 on normal mounts.

`btrfs_set_free_space_cache_settings()` derives runtime free-space cache settings from on-disk state and mount options. It forces free-space tree when sector size differs from page size and clears old space cache on zoned filesystems.

`set_device_specific_options()` auto-enables SSD optimization on non-rotational devices and auto-enables async discard on discardable non-zoned devices unless discard was explicitly configured or disabled.

`btrfs_clear_oneshot_options()` removes mount-only flags such as backup-root use and cache-clearing after mount/remount processing.

`btrfs_emit_options()` logs newly enabled/disabled options and compression changes.

## Subvolume Resolution And Mounting

`btrfs_get_subvol_name_from_objectid()` reconstructs a subvolume path by walking root backrefs in the root tree and inode refs in parent filesystem trees until it reaches the top-level subvolume. It returns a `PATH_MAX`-bounded allocated path.

`get_default_subvol_objectid()` looks up the `"default"` dir item under `btrfs_super_root_dir()` and falls back to `BTRFS_FS_TREE_OBJECTID` if not found.

`mount_subvol()` resolves the requested or default subvolume, calls `mount_subtree()`, verifies that the resulting root inode is a subvolume inode, and checks that a requested objectid matches the mounted root.

`btrfs_get_tree_subvol()` creates a temporary `btrfs_fs_info`, duplicates the fs_context for mounting the whole filesystem, then creates a vfsmount and switches `fc->root` to the requested subvolume dentry.

A long comment explains the historical complexity of allowing different read-only/read-write states per Btrfs subvolume mount, especially the ambiguity between mount read-only and superblock read-only in the old mount API and compatibility expectations with modern mount tooling.

## Superblock Filling And Sync

`btrfs_fill_super()` initializes the VFS superblock:

- Sets max file size, magic, super operations, dentry ops, export ops, verity ops, xattrs, time granularity, and cgroup/writeback flags.
- Sets up backing device info.
- Calls `open_ctree()` to open the filesystem.
- Emits mount options.
- Loads the root inode and creates `sb->s_root`.
- Marks the superblock active.

`btrfs_put_super()` logs the last unmount and calls `close_ctree()`.

`btrfs_sync_fs()` handles `sync_fs`:

- Non-waiting sync flushes btree inode mapping.
- Waiting sync waits ordered roots, attaches to or starts a transaction when needed, handles frozen filesystems carefully, and commits the transaction.

## Remount And Reconfigure

`btrfs_info_to_ctx()` and `btrfs_ctx_to_info()` copy mount option state between `btrfs_fs_info` and `btrfs_fs_context`.

`btrfs_reconfigure()` handles remounts and mount reconfiguration. It:

- Saves old context.
- For mount reconfiguration, preserves existing mount options except ro/rw/subvolume changes.
- Syncs the filesystem.
- Marks `BTRFS_FS_STATE_REMOUNTING`.
- Validates options and feature compatibility.
- Applies new context.
- Handles autodefrag cleanup, thread-pool resizing, and free-space-tree transition restrictions.
- Switches read-write to read-only or read-only to read-write when requested.
- Updates ACL masks, emits option logs, wakes the transaction thread, runs cleanup, clears one-shot options, and clears remounting state.
- Restores old context on later failure.

`btrfs_remount_rw()` rejects remounting read-write after filesystem error, without writable devices, without enough devices for the RAID profile, or when tree-log replay would be required. It then runs pre-RW setup, clears read-only state, marks the filesystem open, and resumes discard.

`btrfs_remount_ro()` cancels reclaim workers, cleans discard, waits for UUID rescan, sets read-only state, deletes unused block groups, waits for cleaner state, runs delayed iputs, suspends device replace, cancels scrub, pauses balance, waits for qgroup rescan, and commits the superblock.

`btrfs_remount_begin()` and `btrfs_remount_cleanup()` handle autodefrag wait/cleanup, discard toggle handling, and old space-cache state toggles.

## Mounting The Superblock

`btrfs_get_tree_super()` scans the source device, locates/holds `fs_devices`, calls `sget_fc()`, and either reuses an existing superblock or opens devices and fills a new one.

For a new mount it:

- Opens devices with mode derived from requested read-only/read-write flags.
- Rejects read-write mount without writable devices.
- Applies device-specific options.
- Sets `sb->s_id`.
- Renames shrinker debugfs entry.
- Calls `btrfs_fill_super()`.

For an existing superblock it drops the temporary fs_devices hold and leaves read-only mismatches to later reconfiguration.

`btrfs_fc_test_super()` matches superblocks by `fs_devices`.

`btrfs_get_tree()` delegates to subvolume mounting.

`btrfs_kill_super()` kills the anonymous superblock and frees `fs_info`.

`btrfs_free_fs_context()` frees duplicated context state and any temporary `fs_info`.

`btrfs_dup_fs_context()` shares the Btrfs fs-private context by refcount and transfers the source string to the duplicate context.

`btrfs_init_fs_context()` initializes defaults, hooks `btrfs_fs_context_ops`, and sets default ACL and inode-version flags.

`btrfs_fs_type` registers the filesystem as `"btrfs"` with device requirement, binary mount data, idmapped mounts, and mtime-granularity support.

## `statfs` And Space Reporting

`btrfs_calc_avail_data_space()` simulates chunk allocation availability across open devices. It filters usable devices, accounts for RAID profile stripe requirements, sorts devices by available bytes, and accumulates allocatable data space.

`btrfs_statfs()` reports filesystem space. It:

- Aggregates data free space, metadata free space, and total disk-used bytes from all space infos.
- Accounts readonly block groups through `btrfs_account_ro_block_groups_free_space()`.
- Applies RAID factor scaling.
- Subtracts the global block reserve from free blocks.
- Adds simulated unallocated data chunk space.
- Sets `f_bavail` to zero if metadata space is exhausted and the global reserve cannot fit.
- Fills magic, block size, name length, and fsid values, including subvolume root id to disambiguate subvolume mounts.

## Freeze, Unfreeze, And Superblock Integrity

`btrfs_freeze()` marks the filesystem frozen and commits the current transaction.

`check_dev_super()` reads the primary superblock from a device while frozen and verifies checksum type, checksum, structural validity, and transaction generation against the committed transaction.

`btrfs_unfreeze()` checks every present device superblock for unexpected modification, reports filesystem error if any device changed, clears frozen state, and returns success so VFS can thaw even if the filesystem was forced read-only.

## Control Device And Device Events

`btrfs_control_open()` initializes control file private data.

`btrfs_control_ioctl()` implements `/dev/btrfs-control` ioctls, restricted to `CAP_SYS_ADMIN`:

- `BTRFS_IOC_SCAN_DEV`
- `BTRFS_IOC_FORGET_DEV`
- `BTRFS_IOC_DEVICES_READY`
- `BTRFS_IOC_GET_SUPPORTED_FEATURES`

It copies and validates user volume args, scans devices under `uuid_mutex`, forgets devices by path/devt, reports readiness, or returns supported feature data.

`btrfs_remove_bdev()` handles block-device disappearance. It finds the Btrfs device, marks it missing, updates writable/missing counters, checks whether the filesystem can remain read-write in degraded mode, and either returns `-EIO` or sets the degraded mount option.

`btrfs_shutdown()` forces filesystem shutdown.

## Super Operations And Shrinker Hooks

`btrfs_super_ops` provides VFS callbacks:

- inode drop/evict/allocation/destruction/free
- `put_super`
- `sync_fs`
- mount option and device-name display
- `statfs`
- freeze/unfreeze
- cached object counting/freeing
- stats display
- block device removal
- shutdown

`btrfs_show_options()` emits mount options for `/proc/mounts`, including subvolid and reconstructed subvolume path.

`btrfs_show_devname()` prints the latest device name under RCU.

`btrfs_nr_cached_objects()` reports evictable extent maps to the shrinker.

`btrfs_free_cached_objects()` asks extent-map code to free cached objects and returns zero because freeing is asynchronous.

`btrfs_show_stats()` currently emits zoned stats for zoned filesystems.

## Module Initialization And Exit

`btrfs_ctl_fops` and `btrfs_misc` register `/dev/btrfs-control`.

`btrfs_print_mod_info()` prints compile-time feature status such as experimental, debug, assert, zoned, and fsverity support.

`mod_init_seq[]` centralizes initialization and cleanup order for properties, sysfs, compression, caches, DIO, transactions, ctree, free space, extent state, extent buffers, biosets, extent maps, optional read policy, ordered data, delayed inode, auto defrag, delayed refs, prelim refs, control device, sanity tests, and filesystem registration.

`init_btrfs_fs()` runs the sequence and unwinds on failure.

`btrfs_exit_btrfs_fs()` unwinds successful init steps in reverse order.

`exit_btrfs_fs()` also cleans filesystem UUID state.

The module uses `late_initcall(init_btrfs_fs)` and `module_exit(exit_btrfs_fs)`.

## Concurrency And Locking

Mount-time device discovery and device state changes use `uuid_mutex` and device-list locks.

Subvolume mount compatibility paths coordinate with `s_umount`.

Remount paths set `BTRFS_FS_STATE_REMOUNTING` to inform other subsystems, including space reclaim.

Read-only transition cancels reclaim workers and coordinates with cleaner, scrub, balance, device replace, delayed iputs, UUID rescan, and qgroup rescan.

Freeze/unfreeze relies on the filesystem being frozen to safely inspect device superblocks without device-list locking.

RCU protects latest-device name display.

## Integration Points

`super.c` integrates almost every Btrfs subsystem:

- `disk-io` for `open_ctree()` and `close_ctree()`.
- Transaction, delayed refs, delayed inode, and ordered-data subsystems for sync/remount.
- Space-info and block-group code for statfs and reclaim worker shutdown.
- Device/volume scanning and degraded checks.
- Free-space cache/tree, discard, zoned mode, scrub, qgroup, balance, and dev-replace.
- Compression, verity, xattr, export, inode, and dentry operations.
- Sysfs, module init, miscdevice control, and tracepoints.

## Risks And Edge Cases

Mount option interactions are dense: compression, datacow, datasum, space cache, rescue mode, discard, and ACL behavior all have cross-effects.

Subvolume mounting must preserve old ABI behavior around read-only flags while using the new mount API.

`statfs` is necessarily approximate for mixed RAID profiles and metadata exhaustion thresholds.

Remount read-only has many asynchronous subsystems to quiesce; missing one can leave open transactions or post-RO writes.

Device disappearance handling must distinguish tolerable degraded operation from losing read-write viability.

Freeze/unfreeze protects against external modification after hibernation-like scenarios by validating device superblocks.

## Testing Signals

Useful tests should cover:

- Mount option parsing, negation, aliases, and invalid values.
- Compression type/level parsing.
- Rescue options requiring read-only mounts.
- Free-space cache v1/v2 compatibility and forced free-space tree for subpage sectors.
- Subvolume mounting by name, objectid, default subvolume, and mismatch cases.
- Remount ro/rw transitions, especially degraded and log-replay cases.
- `statfs` under metadata exhaustion, readonly block groups, and multiple RAID profiles.
- `/dev/btrfs-control` ioctls and permission checks.
- Freeze/unfreeze superblock modification detection.
- Device removal degraded/read-write viability handling.
- Module init unwind on intermediate failure.
