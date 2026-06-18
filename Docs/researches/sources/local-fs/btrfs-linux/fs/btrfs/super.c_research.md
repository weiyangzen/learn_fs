# File Research: sources/local-fs/btrfs-linux/fs/btrfs/super.c

This file implements Btrfs VFS superblock integration: filesystem type registration, new mount API context handling, mount option parsing and reporting, subvolume mounting, remount transitions, `statfs`, sync/freeze/unfreeze, `/dev/btrfs-control` ioctls, super operations, shrinker hooks, device removal handling, and module init/exit sequencing.

Mount context and option parsing:
- `struct btrfs_fs_context` stores mount-time context: subvolume name/objectid, inline extent limit, commit interval, metadata ratio, thread pool size, mount option bits, compression type/level, and refcount.
- `btrfs_fs_parameters` describes supported new-mount-API parameters, including ACL, compression, COW/checksum, device scan, discard, free-space cache, subvolume selection, rescue options, and debug options.
- `btrfs_parse_compress()` accepts bare `compress`, typed compression, optional zlib/zstd levels, `compress-force`, and `no`/`none`; enabling compression clears NODATACOW/NODATASUM.
- `btrfs_parse_param()` maps parsed options to context bits and values, scans `device=`, handles rescue aliases/deprecations, validates thread pool size, maps `subvolid=0` to the top-level subvolume, and gates ACL support on `CONFIG_BTRFS_FS_POSIX_ACL`.
- Debug-only options include fragmentation, reference verification, and reference tracking under `CONFIG_BTRFS_DEBUG`.

Option validation and defaults:
- `btrfs_check_options()` rejects rescue/log-replay-ignore options on read-write mounts, prevents disabling the free-space tree when required by on-disk features, delegates zoned option validation, and warns about deprecated space cache v1.
- `btrfs_set_free_space_cache_settings()` reconciles mount options with on-disk free-space-cache state, forces free-space tree for sectorsize/page-size mismatch, clears v1 cache on zoned filesystems, and auto-selects v1 or v2 when the user did not specify a policy.
- `set_device_specific_options()` enables SSD optimizations for non-rotational devices unless disabled and auto-enables async discard on discard-capable non-zoned devices unless discard was explicitly configured.
- `btrfs_clear_oneshot_options()` clears mount-only options that should not persist across remount display/state.
- `btrfs_emit_options()` logs option transitions and current compression/max-inline settings.
- `btrfs_show_options()` emits `/proc/mounts` options including compression, rescue options, cache mode, discard, ACL, subvolume id, and resolved subvolume path.

Mount and subvolume flow:
- `btrfs_init_fs_context()` allocates the Btrfs fs context, installs operations, initializes defaults for new mounts, copies current info for reconfigure, and sets POSIX ACL/I_VERSION flags.
- `btrfs_dup_fs_context()` shares the private context between original and duplicated fs contexts while transferring `source` ownership to the duplicate used for the real superblock mount.
- `btrfs_get_tree_subvol()` allocates a preliminary `btrfs_fs_info`, duplicates the fs context, mounts or finds the real superblock through `btrfs_get_tree_super()`, handles compatibility reconfiguration for ro/rw subvolume mounts, creates a vfsmount, and switches `fc->root` to the requested subvolume dentry.
- `btrfs_get_tree_super()` scans the source device, safely pins `fs_devices` around `sget_fc()`, reuses existing superblocks when available, opens devices for first mounts, applies device-specific options, fills the superblock, and returns a root dentry.
- `btrfs_fill_super()` initializes VFS superblock operations/export/xattr/verity fields, sets up the backing device info, calls `open_ctree()`, emits options, creates the root inode dentry, and marks the superblock active.
- `mount_subvol()` resolves default subvolume objectid when needed, converts subvolid to a path, calls `mount_subtree()`, verifies the resulting inode is a subvolume inode, and checks subvolid/path consistency to catch rename races.
- `btrfs_get_subvol_name_from_objectid()` walks root backrefs and inode refs backwards to reconstruct an absolute subvolume path.
- `get_default_subvol_objectid()` looks up the `default` dir item in the tree of tree roots.

Remount/reconfigure:
- `btrfs_reconfigure()` synchronizes the filesystem, marks remounting, validates options/features, copies context to fs_info, handles thread-pool resizing, manages free-space-tree transition constraints, performs ro/rw transitions, updates POSIX ACL masks, emits option changes, wakes the transaction thread, runs cleanup, and clears remounting state.
- `btrfs_reconfigure_for_mount()` preserves compatibility for subvolume mounts that need to turn an existing read-only superblock back to read-write.
- `btrfs_remount_rw()` rejects remount after fatal errors, no writable devices, non-degradable device sets, or pending log replay; then runs pre-rw mount setup, clears readonly state, marks the fs open, and resumes discard.
- `btrfs_remount_ro()` cancels async reclaim work, cleans discard, waits for UUID scan, marks readonly, deletes unused block groups, waits for cleaner state, runs delayed iputs, suspends dev-replace/scrub/balance/qgroup work, and commits the super.
- `btrfs_remount_begin()` and `btrfs_remount_cleanup()` handle autodefrag shutdown, discard async toggles, and space-cache v1 active-state changes.
- `btrfs_resize_thread_pool()` updates Btrfs worker pools and relevant kernel workqueue max-active values.

Sync, statfs, and VFS operations:
- `btrfs_sync_fs()` flushes btree inode pages for non-wait sync, waits ordered roots for wait sync, attaches to or starts a transaction when needed, and commits it.
- `btrfs_calc_avail_data_space()` simulates the chunk allocator over devices sorted by free bytes to estimate additional data space available for `statfs`.
- `btrfs_statfs()` reports blocks/free/available space, accounts RAID profile factors, readonly block group free space, global block reserve, metadata exhaustion heuristics, sectorsize, name length, and a stable fsid mixed with subvolume root id.
- `btrfs_show_devname()` reports the latest device path under RCU.
- `btrfs_show_stats()` emits zoned stats for zoned filesystems.
- `btrfs_super_ops` wires Btrfs into VFS operations for inode lifecycle, put_super, sync, options, devname, statfs, freeze/unfreeze, shrinker object count/free, stats, block-device removal, and shutdown.

Freeze, unfreeze, and device safety:
- `btrfs_freeze()` sets `BTRFS_FS_FROZEN` and commits the current transaction.
- `check_dev_super()` rereads each present device's primary superblock while frozen, verifies checksum type, checksum, superblock validity, and committed generation.
- `btrfs_unfreeze()` checks all devices for unexpected modification, handles errors by forcing filesystem error/readonly state, then clears frozen state while still returning success to the VFS so thaw can finish.
- `btrfs_remove_bdev()` handles lower block-device removal notifications by marking the matching Btrfs device missing, updating writable/missing counts, checking whether read-write degraded operation remains possible, and setting DEGRADED when continuing.
- `btrfs_shutdown()` forces filesystem shutdown.

Control device and module lifecycle:
- `/dev/btrfs-control` is registered as a misc device with `btrfs_ctl_fops`.
- `btrfs_control_ioctl()` requires `CAP_SYS_ADMIN` and supports device scan, forget device, devices-ready query, and supported-feature query.
- `btrfs_interface_init()`/`btrfs_interface_exit()` register and unregister the control device.
- `btrfs_print_mod_info()` prints module feature flags such as experimental, debug, assert, zoned, fsverity, and read policy.
- `mod_init_seq` orders initialization of properties, sysfs, compression, caches, direct I/O, transactions, ctree, free-space caches, extent state/buffer caches, biosets, extent maps, optional read policy, ordered data, delayed inode/ref infrastructure, backrefs, control interface, sanity tests, and filesystem registration.
- `btrfs_exit_btrfs_fs()` unwinds successfully initialized components in reverse order; `exit_btrfs_fs()` also cleans up filesystem UUID tracking.
- `late_initcall(init_btrfs_fs)` registers the filesystem late in boot, and `module_exit(exit_btrfs_fs)` handles module unload.

Cross-file relationships:
- `disk-io.c` provides `open_ctree()`/`close_ctree()` and filesystem initialization/teardown internals.
- `transaction.c`, `ordered-data.c`, `delayed-inode.c`, `dev-replace.c`, `scrub.c`, `qgroup.c`, `discard.c`, and `block-group.c` are coordinated during sync, remount, freeze, and readonly transitions.
- `space-info.c` supplies readonly block group accounting and async reclaim work that this file cancels on readonly remount.
- `volumes.c` provides device scan/open/forget, degraded checks, device lookup, and allocator profile information.
- `compression.c` provides compression type/level parsing and display.
- `zoned.c` validates zoned mount options and reports zoned stats.
- `ioctl.c` supplies ioctl feature reporting and volume-argument path validation for the control device.

Important invariants and risks:
- The Btrfs subvolume mount path deliberately uses a duplicated fs context and a temporary mount because VFS superblock state and mount read-only state are distinct but must remain compatible with legacy mount behavior.
- `uuid_mutex` must not be held across `sget_fc()`; the code pins `fs_devices` to bridge that lifetime gap.
- Rescue options that bypass normal replay/checking are read-only only.
- Read-write remount is forbidden after filesystem error, insufficient writable devices, non-degradable device loss, or unreplayed tree log.
- Freeze/unfreeze superblock generation checks protect against hibernation or external modification while frozen.
- `statfs` availability is intentionally pessimistic and zeroes `f_bavail` when metadata is effectively exhausted.
- Module init uses a table-driven sequence so partial initialization failures unwind only completed stages.
