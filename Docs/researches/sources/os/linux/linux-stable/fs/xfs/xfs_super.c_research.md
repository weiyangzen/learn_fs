# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_super.c

Main Linux VFS integration file for XFS. It handles mount option parsing, device setup, superblock operations, mount/remount lifecycle, per-mount resources, module initialization, and module teardown.

Major responsibilities:
- Defines the XFS `file_system_type` and `fs_context_operations`.
- Implements `super_operations` for inode destruction, syncing, freeze/thaw, statfs, shrinker hooks, shutdown, mount option display, filesystem stats, and error reporting.
- Performs full mount setup in `xfs_fs_fill_super`.
- Performs remount transitions in `xfs_fs_reconfigure`, `xfs_remount_rw`, and `xfs_remount_ro`.
- Initializes and destroys global caches, workqueues, procfs, sysctl, debugfs, sysfs, quota, and filesystem registration.

Mount option handling:
- `xfs_fs_parameters` declares supported options: log sizing/devices, realtime device, sync/noalign/swalloc, stripe geometry, UUID behavior, inode32/inode64, largeio, filestreams, quota variants, discard, DAX, zoned options, lifetime behavior, atomic write size, and debug errortags.
- `attr2`, `noattr2`, `ikeep`, and `noikeep` are parsed as deprecated options with explicit warnings.
- `xfs_fs_parse_param` mutates the parsing mount structure according to options.
- `xfs_fs_validate_params` rejects invalid combinations such as `norecovery` on rw mounts, `noalign` with stripe geometry, quota options without quota support, incomplete stripe geometry, invalid log buffer sizes, and invalid allocation sizes.
- `xfs_finish_flags` validates constraints after the on-disk superblock has been read, including log stripe constraints, readonly filesystem flags, quota compatibility, and zoned-only option restrictions.

Mount setup flow:
- `xfs_init_fs_context` allocates and initializes `struct xfs_mount`, xarrays, locks, delayed work, defaults, hooks, and the fs_context operations.
- `xfs_fs_get_tree` delegates to `get_tree_bdev`.
- `xfs_fs_fill_super` copies VFS mount flags, validates parameters, opens devices, creates debugfs entries, allocates per-mount workqueues/counters/inodegc/stats, reads the XFS superblock, configures devices, checks deprecated/unsupported features, validates page-cache/file-size limits, reads realtime metadata, starts filestream support, configures VFS superblock fields, validates DAX/discard/zoned/reflink constraints, resumes quota settings, runs `xfs_mountfs`, and installs the root dentry.
- Error paths unwind in reverse order: filestream, realtime superblock, main superblock, scrub stats, stats, inodegc, counters, workqueues, and devices.

Device handling:
- `xfs_open_devices` opens external log and realtime devices, rejects duplicate realtime/data/log device combinations, and creates buftargs.
- `xfs_setup_devices` configures data, log, and realtime buftargs from superblock geometry.
- `xfs_shutdown_devices` flushes and invalidates block devices on unmount to avoid stale bdev pagecache interactions with tools such as blkid and xfs_db.

Inode and VFS operations:
- `xfs_fs_alloc_inode` deliberately `BUG()`s because XFS uses its own inode allocation path.
- `xfs_fs_destroy_inode` increments inode destruction stats and marks the XFS inode reclaimable.
- `xfs_fs_drop_inode` preserves inodes still involved in log recovery.
- `xfs_fs_evict_inode` breaks final DAX layouts, truncates pagecache, clears VFS inode state, and releases zoned open-zone state for regular files.
- `xfs_fs_sync_fs` forces the log and, during freeze, stops inodegc, blockgc, and zonegc.
- `xfs_fs_freeze` saves reserve blocks and quiesces the log under `GFP_NOFS`.
- `xfs_fs_unfreeze` restores reservations and restarts background workers for writable filesystems.
- `xfs_fs_statfs` reports data or realtime free space depending on inode flags, applies project quota statvfs behavior, and reports no distinction between privileged/unprivileged free blocks.

Per-mount resources:
- Workqueues: buffer, unwritten conversion, reclaim, blockgc, inodegc, and sync.
- Per-CPU counters: inode counts, free inode counts, delayed allocation blocks, delayed realtime extents, and free-space counters.
- Per-CPU inodegc state is allocated and initialized per possible CPU.
- `xfs_fs_put_super` performs unmount cleanup before `xfs_mount_free` releases device targets and strings.

Remount behavior:
- `xfs_remount_rw` rejects rw transition if external log/rt devices are readonly, if mounted `norecovery`, or if unknown ro-compatible features exist. It restores reservations, restarts log/blockgc/inodegc/zonegc, and reserves per-AG blocks.
- `xfs_remount_ro` syncs the filesystem, stops blockgc/inodegc/zonegc, frees COW/speculative prealloc space, unreserves per-AG blocks, saves reserve blocks, cleans the log, and marks the mount readonly.
- `xfs_fs_reconfigure` validates new parsed options, copies errortags, applies atomic write option changes, handles inode32/inode64 transitions, reruns finish validation, and performs ro/rw transitions.

Global module lifecycle:
- `xfs_init_caches` creates slab caches for buffers, log tickets, btree cursors, deferred items, dir attr state, iforks, transactions, log items, inode structures, quota/log recovery item families, exchange-map items, and parent args.
- `xfs_destroy_caches` destroys them after `rcu_barrier`.
- `xfs_init_workqueues` creates global allocation and discard workqueues.
- `init_xfs_fs` checks on-disk structures, runs dir hash tests, prints build options, starts directory support, initializes caches/workqueues/MRU/procfs/sysctl/debugfs/sysfs/global stats/debug attrs/quota, and registers the filesystem.
- `exit_xfs_fs` reverses global initialization and unregisters the filesystem.

Important exported/local interfaces:
- `xfs_set_inode_alloc` updates per-AG inode allocation policy for inode32/inode64 behavior.
- `xfs_flush_inodes` synchronously schedules inode writeback via per-mount sync workqueue.
- `xfs_debugfs_mkdir` wraps debugfs directory creation.
- Module hooks are `module_init(init_xfs_fs)` and `module_exit(exit_xfs_fs)`.

Research notes:
- This file is the coordination hub for many XFS subsystems; changes here have broad mount/unmount and error-path blast radius.
- Error unwinding is carefully ordered and should be preserved when adding resources.
- Mount parsing happens before `mp->m_super` is available; code in `xfs_fs_parse_param` must not depend on a live superblock.
- Feature validation is split between pre-superblock option validation and post-superblock checks that require on-disk geometry/features.
