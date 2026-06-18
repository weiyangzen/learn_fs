# File Research: sources/os/linux/linux-stable/fs/btrfs/super.c

This file implements Btrfs VFS superblock integration, mount option parsing, fs-context operations, subvolume mounting, remount handling, statfs accounting, control-device ioctls, freeze/unfreeze behavior, superblock operations, filesystem registration, and module init/exit sequencing.

Mount context and options:
- `struct btrfs_fs_context` stores parsed mount state before it is copied into `btrfs_fs_info`.
- `btrfs_fs_parameters[]` defines the new mount API parameter table for options such as compression, discard, space cache, rescue modes, subvolume selection, degraded mounts, thread pool size, and debugging options.
- `btrfs_parse_param()` maps parsed options into mount flags and context fields.
- Compression parsing supports `zlib`, `lzo`, `zstd`, optional levels where supported, `compress-force`, and disabling compression with `no` or `none`.
- Rescue options include backup root, no log replay, ignoring bad roots, ignoring data or metadata checksums, ignoring super flags, and `rescue=all`.
- Deprecated compatibility options such as `usebackuproot` and `norecovery` are preserved with warnings or compatibility messages.

Option validation and defaults:
- `btrfs_check_options()` rejects writeable mounts with read-only-only rescue options and prevents invalid free-space-tree combinations.
- It delegates zoned-specific mount option validation to `btrfs_check_mountopts_zoned()`.
- `btrfs_set_free_space_cache_settings()` chooses free-space-cache behavior from explicit options, on-disk feature state, page/sector size constraints, and zoned mode.
- `set_device_specific_options()` auto-enables SSD optimizations and async discard when devices support it and the user did not override it.
- One-shot options such as backup root and clear cache are cleared after mount/remount processing.

Subvolume naming and selection:
- `btrfs_get_subvol_name_from_objectid()` reconstructs a subvolume path by walking root backrefs in the root tree and inode refs in filesystem trees.
- `get_default_subvol_objectid()` resolves the default subvolume from the root directory’s `default` item, falling back to the top-level subvolume.
- `mount_subvol()` mounts a selected subvolume path, verifies the root inode is a subvolume inode, and checks that `subvolid` matches when supplied.

Superblock fill and sync:
- `btrfs_fill_super()` initializes VFS superblock fields, sets operations, export ops, xattrs, verity ops when enabled, backing device info, opens the Btrfs tree, emits options, and creates the root dentry.
- `btrfs_sync_fs()` flushes btree inode mapping for non-wait syncs, waits ordered roots for wait syncs, attaches or starts a transaction if needed, and commits it.

Show options:
- `btrfs_show_options()` emits the effective mount options for `/proc/mounts`, including compression, rescue flags, discard mode, ACL state, space cache state, subvolume id, and subvolume path.
- `print_rescue_option()` formats multiple rescue flags under a single `rescue=` option group.

Remount/reconfigure:
- `btrfs_reconfigure()` implements fs-context reconfiguration and remount behavior.
- It preserves mount options during bind-style subvolume reconfiguration, syncs the filesystem, sets remounting state, validates options and features, resizes worker pools, transitions read-only/read-write state, emits changed options, wakes the transaction thread, and cleans up one-shot state.
- `btrfs_remount_rw()` prevents writeable remount after fs error, without writeable devices, when not degradable enough, or when log replay would be required.
- `btrfs_remount_ro()` cancels reclaim work, stops discard, waits for UUID rescan, sets readonly state, deletes unused block groups, waits for cleaner work, runs delayed iputs, suspends dev-replace, cancels scrub, pauses balance, waits qgroup rescan, and commits the superblock.
- `btrfs_remount_begin()` and `btrfs_remount_cleanup()` coordinate autodefrag, discard, and space-cache side effects.

`statfs` accounting:
- `btrfs_calc_avail_data_space()` simulates data chunk allocation across devices sorted by maximum available space and RAID profile constraints.
- `btrfs_statfs()` reports total blocks, free blocks, available blocks, block size, name length, and fsid.
- It accounts for global block reserve, readonly block group free space, RAID profile factors, mixed metadata/data mode, and metadata exhaustion heuristics.

Mount API and subvolume mount mechanics:
- `btrfs_get_tree_super()` scans the source device, finds or creates a VFS superblock with `sget_fc()`, opens devices for first mounts, fills the superblock, and reuses existing superblocks for subsequent mounts.
- `btrfs_get_tree_subvol()` creates a duplicated fs context for the real superblock mount, then mounts the requested subvolume as the caller’s root.
- `btrfs_reconfigure_for_mount()` preserves compatibility for per-subvolume ro/rw behavior by converting a reused read-only superblock back to read-write when needed.
- `btrfs_dup_fs_context()` shares the Btrfs fs context across duplicated fs contexts and transfers `source` ownership carefully.
- `btrfs_free_fs_context()` releases partially initialized fs-info and refcounted mount context state.

Filesystem type and control device:
- `btrfs_fs_type` registers Btrfs with the VFS using fs-context operations and flags requiring a block device, binary mount data, idmapped mounts, and multigrain timestamps.
- `/dev/btrfs-control` is registered as a misc device.
- `btrfs_control_ioctl()` supports:
  - scanning a device,
  - forgetting devices,
  - checking whether devices are ready,
  - returning supported feature flags.
- Control ioctls require `CAP_SYS_ADMIN`.

Freeze/unfreeze and device integrity:
- `btrfs_freeze()` marks the fs frozen and commits the current transaction.
- `btrfs_unfreeze()` checks every device’s primary superblock for checksum, superblock validity, checksum type, fsid validity, and generation consistency before clearing frozen state.
- `check_dev_super()` performs the per-device validation and returns `-EUCLEAN` on detected unexpected modification.

Super operations:
- `btrfs_super_ops` wires Btrfs into VFS operations for inode eviction, sync, option display, device name display, inode allocation/destruction, statfs, freeze/unfreeze, shrinker callbacks, zoned stats, block-device removal, and shutdown.
- `btrfs_remove_bdev()` marks a removed block device missing, updates writable device accounting, checks degradability, and either continues degraded or fails read-write operation.
- `btrfs_shutdown()` forces filesystem shutdown.
- Shrinker callbacks count and free cached extent maps.

Module initialization:
- `mod_init_seq[]` defines ordered init/exit pairs for properties, sysfs, compression, caches, direct I/O, transactions, ctree, free-space cache, extent states, extent buffers, biosets, extent maps, ordered data, delayed inode/ref infrastructure, auto defrag, preliminary refs, control interface, sanity tests, and filesystem registration.
- `init_btrfs_fs()` runs the sequence and unwinds already initialized steps on failure.
- `exit_btrfs_fs()` reverses initialized steps and cleans up filesystem UUID state.
- Module metadata declares Btrfs description and GPL license.
