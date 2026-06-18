# File Research: sources/os/linux/linux/fs/xfs/xfs_super.c

## Purpose

`xfs_super.c` is the Linux VFS integration and module lifecycle implementation for XFS. It handles mount option parsing, filesystem context setup, block device opening, per-mount workqueue and counter initialization, superblock validation, VFS super operations, remount transitions, cache creation/destruction, global sysfs/procfs/debugfs setup, and module registration.

## Top-Level State

- `xfs_super_operations`: VFS superblock callbacks for inode lifecycle, sync, freeze, statfs, unmount, shrinker, shutdown, stats, and error reporting.
- `xfs_debugfs`: top-level debugfs directory for XFS.
- `xfs_kset`: top-level sysfs kset under `/sys/fs/xfs`.
- `xfs_dbg_kobj`: debug-only global sysfs object.
- `xfs_fs_type`: Linux `file_system_type` registered as `"xfs"`.
- `xfs_discard_wq`, `xfs_alloc_wq`: global workqueues initialized at module load.

## Mount Option Parsing

- Defines table-driven fs parameters in `xfs_fs_parameters`.
- Supports core options such as `logbufs`, `logbsize`, `logdev`, `rtdev`, `wsync`, `noalign`, `swalloc`, `sunit`, `swidth`, `nouuid`, `inode32`, `inode64`, `largeio`, `filestreams`, quota options, `discard`, DAX options, zoned options, lifetime controls, max atomic write size, and debug errortags.
- Deprecates `attr2`, `noattr2`, `ikeep`, and `noikeep`, with loud warnings and deprecation postponed to September 2030.
- `suffix_kstrtoint` and `suffix_kstrtoull` parse K/M/G suffixes for size options.
- `xfs_fs_parse_param` writes parsed state into the temporary `struct xfs_mount` stored in `fs_context->s_fs_info`. It sets feature bits, quota flags, names for external devices, DAX mode, max open zones, and atomic write limits.
- `xfs_fs_validate_params` rejects incompatible combinations such as `norecovery` without read-only, `noalign` with stripe settings, quota options without quota support, invalid stripe settings, invalid log buffer counts/sizes, and invalid allocation size.

## Device Setup

- `xfs_blkdev_get` opens external log or realtime devices using the superblock open mode.
- `xfs_open_devices` opens external log/realtime devices, rejects identical realtime and data/log devices, and allocates buffer targets for data, log, and realtime devices.
- `xfs_setup_devices` configures buffer targets after the on-disk superblock is read, including log sector size, internal realtime handling, and external realtime size.
- `xfs_shutdown_devices` flushes and invalidates data, log, and realtime block devices during teardown to avoid stale page-cache metadata after unmount.

## Workqueues, Counters, and Inode GC

- `xfs_init_mount_workqueues` creates per-mount workqueues for buffer I/O, unwritten extent conversion, inode reclaim, speculative block GC, inode GC, and sync work.
- `xfs_destroy_mount_workqueues` tears them down in reverse.
- `xfs_flush_inodes_worker` and `xfs_flush_inodes` perform synchronous inode flushing via the sync workqueue.
- `xfs_init_percpu_counters`, `xfs_reinit_percpu_counters`, and `xfs_destroy_percpu_counters` manage free block, inode, delalloc block, and realtime extent counters.
- `xfs_inodegc_init_percpu` allocates and initializes per-CPU inode GC queues and delayed work items.
- `xfs_inodegc_free_percpu` releases inode GC storage.

## VFS Super Operations

- `xfs_fs_alloc_inode` intentionally BUGs because XFS uses its own inode allocation path.
- `xfs_fs_destroy_inode` marks XFS inodes reclaimable and increments destroy counters.
- `xfs_fs_drop_inode` keeps recovery-owned unlinked inodes alive until log recovery handles them.
- `xfs_fs_evict_inode` breaks final DAX layout, truncates inode pages, clears the VFS inode, and releases zoned realtime open-zone references for regular files.
- `xfs_fs_sync_fs` forces the log on synchronous sync, and stops inode/block/zone GC during the pagefault stage of filesystem freeze.
- `xfs_fs_freeze` saves reserve blocks and quiesces the log in a nofs allocation context.
- `xfs_fs_unfreeze` restores reservations, restarts log work, and restarts background GC for read-write mounts.
- `xfs_fs_statfs` reports data or realtime space depending on inode flags, accounts for reserved blocks, reports inode capacity/free counts, and applies project quota limits when relevant.
- `xfs_fs_shutdown` forces shutdown with `SHUTDOWN_DEVICE_REMOVED`.
- `xfs_fs_show_stats` emits zoned stats for zoned realtime filesystems.
- `xfs_fs_report_error` forwards non-metadata inode I/O errors to health monitoring.

## Mount Fill and Validation

- `xfs_fs_fill_super` is the central mount routine used by `get_tree_bdev`.
- It copies VFS flags into XFS mount state, validates parsed options, sets VFS xattr/export/quota/super operations, handles debug mount delay, opens devices, creates debugfs directory, initializes workqueues/counters/inodegc/stats/scrub stats, reads the superblock, finishes flags, and configures devices.
- It rejects unsupported or unsafe states: unsupported V4 filesystems, deprecated ASCII case-insensitive filesystems when support is disabled, `needsrepair` without `norecovery`, in-progress offline operations, block sizes unsupported by page cache or folios, filesystems too large for platform limits, and file offset limits exceeding XFS extent map capacity.
- It initializes realtime superblock state and filestream mount state before configuring VFS superblock fields.
- It sets VFS metadata such as magic, block size, max file size, max links, timestamp range, cgroup writeback, HSM flag, POSIX ACL flag, and inode versioning for v5 superblocks.
- It validates DAX support, disables unsupported discard, enforces zoned realtime requirements, rejects reflink with incompatible realtime extent sizes or zoned realtime devices, and enables debug-only always-COW mode when configured.
- It resumes quota accounting/enforcement from on-disk state if no quota mount options were provided.
- It calls `xfs_mountfs`, obtains the root inode, and installs `sb->s_root`.
- Error paths unwind in staged reverse order: filestream, realtime sb, core sb, scrub stats, stats, inodegc, counters, workqueues, and devices.

## Remount and Filesystem Context

- `xfs_remount_rw` rejects read-write transition when external log/realtime devices are read-only, `norecovery` is set, or unknown ro-compatible features exist. It then clears readonly, writes pending superblock changes, restores reservations, restarts log/blockgc/inodegc/zonegc, and reserves AG metadata blocks.
- `xfs_remount_ro` syncs the filesystem, stops blockgc, frees COW/speculative preallocation state, stops inodegc and zonegc, frees AG metadata reservations, saves reserve blocks, cleans the log, and marks the mount readonly.
- `xfs_fs_reconfigure` applies supported remount changes, validates parameters, copies errortags, updates max atomic write size, handles inode32/inode64 transitions, re-runs finish flag validation, and performs readonly/read-write transitions.
- `xfs_init_fs_context` allocates and initializes a fresh `struct xfs_mount`, including locks, xarrays, work structs, kset linkage, finobt reservation behavior, default log/allocsize values, and directory update hooks.
- `xfs_fs_free` frees an untransferred mount during fs_context cleanup.
- `xfs_kill_sb` delegates to `kill_block_super` and then frees the XFS mount.

## Cache and Module Lifecycle

- `xfs_init_caches` creates slab caches for buffers, log tickets, btree cursors, deferred items, directory/attr state, iforks, transactions, log item types, inodes, inode log items, intent/done item families, unlink items, exchange mapping items, and parent pointer args. Error paths unwind each cache in reverse dependency order.
- `xfs_destroy_caches` waits for delayed RCU frees via `rcu_barrier` and destroys all caches.
- `xfs_init_workqueues` creates global allocation and discard workqueues.
- `xfs_destroy_workqueues` destroys global workqueues.
- `init_xfs_fs` verifies on-disk structure sizes, runs dahash tests, prints build options, starts directory support, initializes caches/workqueues/MRU/procfs/sysctl/debugfs/sysfs/global stats/scrub stats/debug sysfs/quota, and registers the filesystem.
- `exit_xfs_fs` unregisters and tears down quota, filesystem registration, debug sysfs, scrub stats, stats sysfs, global stats storage, kset, debugfs, sysctl, procfs, MRU cache, workqueues, caches, and UUID table.

## Dependencies and Callers

- This file depends on nearly every major XFS subsystem: mount, inode, btree, allocation, log, quota, filestreams, realtime, reflink, zoned allocation, health monitoring, scrub stats, and VFS fs_context APIs.
- Exports or defines functions used externally through `xfs_super.h`, including `xfs_flush_inodes`, `xfs_set_inode_alloc`, `xfs_reinit_percpu_counters`, `xfs_debugfs_mkdir`, and `xfs_discard_wq`.
- Coordinates with `xfs_sysfs.c` for per-mount and global sysfs objects, `xfs_stats.c` for global/per-mount stats storage, and `xfs_sysctl.c` for sysctl registration.

## Research Notes

- This file is the highest-risk integration point in the group. Small changes can affect mount compatibility, recovery safety, block-device lifetime, remount semantics, freeze/thaw behavior, or module unload cleanup.
- Mount validation is deliberately staged: option-only validation occurs before devices and superblock read, while feature compatibility checks occur after the on-disk superblock and realtime metadata are available.
- Teardown is heavily order-dependent because background workers, log state, inode reclaim, buffer targets, sysfs/debugfs objects, and per-CPU allocations all depend on mount lifetime.
