# File Research: sources/os/linux/linux-stable/fs/ext4/super.c

## Purpose

`super.c` is ext4's superblock, mount, remount, journal, quota, sysfs/proc registration, filesystem-type registration, and module lifecycle implementation. It binds ext4 to the VFS through `file_system_type`, `super_operations`, `export_operations`, fs-context parsing, JBD2 journal setup, per-superblock in-memory state, and mount-time validation of on-disk ext4 metadata.

It also supports ext4-as-ext2/ext3 compatibility registration when configured.

## Major Responsibilities

- Register and unregister the ext4 filesystem module, plus optional ext2/ext3 aliases.
- Allocate, initialize, validate, and destroy `struct ext4_sb_info`.
- Read and validate the on-disk ext4 superblock.
- Parse mount/remount options through the modern `fs_context` API.
- Apply default mount policy from the on-disk superblock and explicit user options.
- Validate feature flags, geometry, checksums, group descriptors, inode sizes, cluster sizes, DAX, casefolding, encryption, quota, journaling, and large folio constraints.
- Load internal or external JBD2 journals and configure journal features.
- Manage error reporting, forced read-only state, panic/remount-ro/continue behavior, and superblock error persistence.
- Initialize ext4 subsystems needed per mount: extent status shrinker, multiblock allocator, system zones, orphan tracking, xattr caches, fast commit state, lazy inode-table initialization, per-cpu counters, quota, and proc/sysfs entries.
- Handle freeze/unfreeze, sync, statfs, remount, unmount, and shutdown paths.
- Provide exported helper functions used across ext4 for buffer reads, group descriptor fields, checksums, errors, warnings, quota enablement, and forced commits.

## VFS and Registration Interfaces

- `ext4_fs_type` registers `"ext4"` with `init_fs_context = ext4_init_fs_context`, `parameters = ext4_param_specs`, `kill_sb = ext4_kill_sb`, and flags requiring a block device plus idmapped mounts, multigrain timestamps, and large block size support.
- `ext3_fs_type` is registered as `"ext3"` through the ext4 implementation.
- Optional `ext2_fs_type` is registered when ext4 is configured to handle ext2.
- `ext4_sops` wires inode allocation/free/destruction, writeback, eviction, sync, freeze, unfreeze, statfs, mount-option display, shutdown, and quota I/O into the VFS.
- `ext4_export_ops` supports NFS file handles via generic ino32 encoding and ext4 inode lookup.
- Module init orders subsystem setup carefully: extent-status cache, pending tree, post-read processing, pageio, system zone, sysfs, mballoc, inode cache, fast-commit dentry cache, ext3/ext2 aliases, then ext4 registration.
- Module exit reverses this and stops the lazyinit kthread.

## Mount Context and Option Handling

The file defines `struct ext4_fs_context` as the temporary fs-context state. It stores mount-option bit masks, quota file names, journal device/ioprio, commit interval, stripe, inode readahead, extra inode size, lazyinit multiplier, reserved uid/gid, directory-size limit, debug fast-commit replay limit, and explicit-option markers.

Main option flow:

- `ext4_init_fs_context()` allocates `struct ext4_fs_context`, installs `ext4_context_ops`, and enables `SB_I_VERSION`.
- `ext4_parse_param()` maps fs parameters from `ext4_param_specs` and `ext4_mount_opts` into context masks and scalar fields.
- `parse_options()` handles legacy comma-separated option strings, used for on-disk `s_mount_opts`.
- `parse_apply_sb_mount_options()` applies superblock-stored default mount options before explicit runtime options.
- `ext4_validate_options()` rejects incompatible quota-option combinations.
- `ext4_check_opt_consistency()` enforces ext2/ext3 compatibility restrictions, remount invariants, DAX rules, data journaling immutability on remount, dummy encryption constraints, and quota consistency.
- `ext4_apply_options()` transfers the validated context masks and scalar values into `ext4_sb_info` and `super_block`.
- `_ext4_show_options()` and `ext4_seq_options_show()` emit active options for mountinfo and `/proc/fs/ext4/<dev>/options`.

Important constraints enforced here include no journal device/path changes on remount, no changing data mode on remount, no incompatible DAX transitions on remount, no journal options on no-journal filesystems, and no mixing old quota mount options with journaled quota files.

## Superblock Read and Mount Bring-Up

`ext4_fill_super()` allocates `ext4_sb_info`, sanitizes the device name, selects the superblock block, and calls `__ext4_fill_super()`.

`__ext4_fill_super()` is the main mount pipeline:

1. Set initial defaults such as journal IO priority, inode readahead, write counters, commit/batch intervals, superblock update intervals, and lazyinit multiplier.
2. `ext4_load_super()` reads the ext4 superblock, handles 1 KiB offset alignment, validates magic and block-size fields, and reloads at the actual filesystem block size when needed.
3. `ext4_init_metadata_csum()` validates checksum type, verifies the superblock checksum, sets checksum triggers, and precomputes metadata checksum seed.
4. `ext4_set_def_opts()` applies on-disk default mount options such as ACLs, xattrs, journal checksum, data mode, errors policy, block validity, discard, barrier, delayed allocation, and dioread_nolock.
5. `ext4_inode_info_init()` validates inode size, first inode, timestamp granularity/ranges, and desired extra inode size.
6. Apply superblock-stored mount options, validate user options, apply explicit options, initialize encoding/casefolding, and validate data-journal mode.
7. Validate ext2/ext3/ext4 feature compatibility, DAX, encryption level, descriptor sizes, groups, inode counts, clusters, filesystem geometry, hash seed/version, and group descriptors.
8. Initialize timers, error locks, work items, shrinkers, stripe settings, VFS operations, xattr/encryption/verity/quota operation tables, UUID/sysfs name, orphan list, fast commit state, atomic write support, MMP, and journal.
9. Create xattr caches, calculate overhead clusters, allocate reservation conversion workqueue, load root inode and root dentry, update mount state, reserve clusters, create system-zone metadata, initialize extents, per-cpu counters, mballoc, flex_bg metadata, lazyinit, orphan info, quota tracking, orphan cleanup, recovery completion, discard policy, ratelimits, and sysfs/proc entries.
10. On every failure label, unwind only the initialized subsystems in reverse order.

The mount code is highly defensive: corrupted root inode, bad group descriptors, invalid checksums, unsupported features, inconsistent geometry, unreadable journal, or impossible option combinations abort the mount with explicit cleanup.

## Journal Management

The file supports both internal journal inodes and external journal devices.

Key functions:

- `ext4_get_journal_inode()` validates the internal journal inode exists, is linked, regular, and not encrypted.
- `ext4_open_inode_journal()` initializes a JBD2 journal backed by the journal inode and installs `ext4_journal_bmap()`.
- `ext4_get_journal_blkdev()` opens and validates an external journal block device, including magic, journal-dev incompat flag, checksum, and UUID match.
- `ext4_open_dev_journal()` initializes a JBD2 journal on an external device and rejects external journals with multiple users.
- `ext4_load_journal()` chooses internal or external journal, checks read-only/recovery constraints, wipes or loads JBD2 state, preserves ext4 error fields across journal replay, clears prior journal errors, and updates stored journal dev/inode values if needed.
- `ext4_load_and_init_journal()` sets JBD2 64-bit, checksum, async commit, and fast-commit features, selects default data mode if unspecified, rejects incompatible data/async combinations, sets journal task IO priority, and installs inode data-buffer callbacks.
- `ext4_init_journal_params()` applies commit interval, batch timing, fast commit config, barriers, and cycle recording.
- `ext4_journal_commit_callback()` processes freed data and schedules periodic superblock updates after commits.
- `ext4_force_commit()` exposes a forced JBD2 commit helper.

Data journaling mode has special handling: `data=journal` disables delayed allocation, dioread_nolock, O_DIRECT, and fast commit, and rejects DAX or explicit delalloc conflicts.

## Error Handling and Superblock Updates

The file centralizes ext4 error policy.

Important functions:

- `save_error_info()` records first/last runtime error metadata under `s_error_lock`.
- `ext4_handle_error()` marks `EXT4_ERROR_FS`, aborts the journal unless continuing is allowed, persists error state directly or through deferred work, handles panic policy, and sets emergency read-only state for remount-ro behavior.
- `update_super_work()` writes superblock updates through the journal when possible, or directly as fallback, and notifies sysfs error observers.
- `__ext4_error()`, `__ext4_error_inode()`, `__ext4_error_file()`, `__ext4_std_error()`, `__ext4_warning()`, `__ext4_warning_inode()`, and `__ext4_grp_locked_error()` provide formatted, ratelimited reporting paths for global, inode, file, standard error, warning, and group-locked contexts.
- `ext4_decode_error()` maps kernel errors to human-readable strings.
- `ext4_update_super()` copies in-memory counters, write timestamps, write-kbytes, free blocks/inodes, and accumulated error info into the on-disk superblock buffer and updates its checksum.
- `ext4_commit_super()` writes the superblock synchronously, with optional FUA when barriers are enabled.
- `ext4_mark_recovery_complete()` flushes the journal and clears recovery/orphan feature bits when safe.
- `ext4_clear_journal_err()` transfers prior JBD2 journal error state into the ext4 superblock and clears the journal errno.
- `print_daily_error_info()` periodically logs persistent first/last error details and error counts.

The code treats emergency shutdown/read-only states as early exits in many paths to avoid recursion or unsafe writes.

## Group Descriptor, Geometry, and Checksums

The file owns core superblock-adjacent metadata helpers:

- `ext4_block_bitmap()`, `ext4_inode_bitmap()`, `ext4_inode_table()` and setters combine low/high descriptor fields for 64-bit descriptor support.
- `ext4_free_group_clusters()`, `ext4_free_inodes_count()`, `ext4_used_dirs_count()`, and `ext4_itable_unused_count()` read split descriptor counters.
- `ext4_group_desc_csum()`, `ext4_group_desc_csum_verify()`, and `ext4_group_desc_csum_set()` implement both metadata_csum CRC32C and legacy gdt_csum CRC16 formats.
- `ext4_check_descriptors()` verifies bitmap/inode-table locations, overlap with superblock/GDT areas, group bounds, checksum validity, and tracks the first non-zeroed inode table group.
- `descriptor_loc()` locates group descriptor blocks, including meta_bg and 1 KiB block-size special cases.
- `ext4_block_group_meta_init()` derives descriptor size, blocks/inodes per group, inode-table blocks per group, descriptor counts, max file sizes, and mount state.
- `ext4_handle_clustersize()` validates bigalloc/non-bigalloc cluster geometry and detects standard group size.
- `ext4_check_geometry()` validates reserved GDT size, device addressability, total block count against device size, first data block, group count limit, and inode count consistency.
- `ext4_calculate_overhead()` and `count_overhead()` calculate filesystem overhead clusters, including group metadata and internal journal blocks.
- `ext4_set_resv_clusters()` reserves a small cluster pool for metadata-sensitive operations on extent filesystems.

## Lazy Initialization and Background Work

The file implements global lazy inode-table initialization state:

- `ext4_register_li_request()` registers a per-superblock lazyinit request unless the filesystem is read-only, in emergency state, or has no work.
- `ext4_lazyinit_thread()` runs a global freezable kthread that walks requests, prefetches block bitmaps, zeroes inode tables via `ext4_init_inode_table()`, randomizes retry timing when locks cannot be acquired, and exits when the list is empty.
- `ext4_run_li_request()` switches from bitmap prefetch mode to inode-table initialization mode when appropriate.
- `ext4_unregister_li_request()`, `ext4_remove_li_request()`, `ext4_clear_request_list()`, and `ext4_destroy_lazyinit_thread()` cleanly remove pending work on unmount or module unload.

Lazyinit scheduling is remount-aware and reacts to `init_itable`, read-only state, and `no_prefetch_block_bitmaps`.

## Inode Cache and In-Core Inode Lifecycle

- `init_inodecache()` creates `ext4_inode_cache` with constructor `init_once()`.
- `ext4_alloc_inode()` initializes ext4 inode private state: version, flags, prealloc trees, extent-status tree, reservations, quota fields, JBD2 inode pointer, conversion work, fast-commit tracking, metadata buffer tracking, and locks.
- `ext4_destroy_inode()` warns if an inode is still orphan-tracked or has uncleared reserved data blocks.
- `ext4_free_in_core_inode()` frees fscrypt state and returns the inode to the cache.
- `ext4_clear_inode()` removes fast-commit state, invalidates metadata buffers for no-journal mode, clears VFS inode state, discards preallocations, removes the inode hash before freeing inode bitmap state, clears extents status, drops quotas, releases JBD2 inode state, and frees encryption info.
- `ext4_drop_inode()` delegates to generic drop logic and fscrypt drop rules.

## Remount, Freeze, Sync, and Unmount

- `ext4_sync_fs()` flushes reservation conversion work, writes quota state, starts/waits for JBD2 commits when present, and issues block-device flushes when barriers require it.
- `ext4_freeze()` locks journal updates, flushes the journal, clears recovery/orphan-present bits when safe, and commits the superblock for snapshot consistency.
- `ext4_unfreeze()` restores recovery/orphan-present bits for journaled filesystems and commits the superblock.
- `__ext4_remount()` snapshots old options, validates and applies new options under writeback exclusion where needed, handles read-write to read-only and read-only to read-write transitions, validates group descriptor checksums, rejects unprocessed orphans on rw remount, restarts MMP, adjusts quota state, system-zone state, lazyinit, and abort handling, and rolls back options on failure.
- `ext4_reconfigure()` integrates remount with `fs_context`.
- `ext4_put_super()` unregisters sysfs, stops lazyinit and quotas, destroys workqueues, orphan info, journal, shrinkers, timers, system zones, mballoc, extents, superblock state, group descriptors, flex groups, per-cpu counters, xattr caches, MMP, DAX refs, fscrypt dummy policy, Unicode encoding, kobject state, and `ext4_sb_info`.

Unmount order is deliberate: sysfs is removed before journal destruction and deferred superblock work is flushed only after paths that can enqueue it are disabled.

## Quota Support

When `CONFIG_QUOTA` is enabled, `super.c` defines ext4 quota operations and quotactl hooks.

Covered paths:

- Mount-option parsing for journaled quota file names and formats.
- Consistency checks preventing quota option changes while quotas are loaded and preventing old/new quota mode mixing.
- `ext4_quota_on()` validates same-filesystem quota files, handles journaled quota flags, sets quota inode lockdep class, enables quota, and marks quota files immutable/noatime.
- `ext4_quota_enable()` loads quota tracking from hidden quota inodes used by the quota feature.
- `ext4_enable_quotas()` enables all configured quota types during mount.
- `ext4_quota_off()` forces delayed allocations out, disables quota, and clears quota-file inode flags when possible.
- `ext4_write_dquot()`, `ext4_acquire_dquot()`, `ext4_release_dquot()`, `ext4_mark_dquot_dirty()`, and `ext4_write_info()` wrap quota operations in ext4 journal handles.
- `ext4_quota_read()` and `ext4_quota_write()` provide direct quota file I/O avoiding normal page-cache paths.
- `ext4_statfs_project()` applies project quota limits to statfs results when project inheritance and limits are active.

## Statfs and Reporting

`ext4_statfs()` reports ext4 magic, block size, total blocks minus overhead unless `minixdf` is active, free blocks adjusted for dirty delayed-allocation clusters, available blocks after reserved blocks/clusters, inode counts, name length, and UUID-derived fsid. Project quota limits can cap block and inode availability.

Mount/unmount/remount messages are ratelimited globally, while per-superblock error, warning, and normal messages have independent ratelimit state and counters exposed through sysfs.

## Important Edge Cases and Risks

- Superblock and group-descriptor checksum validation are mount-critical; read-only mounts may tolerate some descriptor overlap/checksum failures that read-write mounts reject.
- Journal recovery requires temporary write access even for read-only mounts; truly read-only devices must use `noload`.
- `data=journal` disables several performance features and conflicts with DAX and explicit delalloc.
- Remount rollback must restore quota names through RCU and restore mount flags under writeback exclusion.
- Error handling avoids taking `s_umount` to set `SB_RDONLY`; it uses ext4 emergency read-only state instead to avoid deadlocks.
- External journals are tightly validated by UUID, superblock feature flags, checksum, block size, and user count.
- Lazyinit must hold mount/write locks opportunistically to avoid racing unmount and freeze.
- Quota operations intentionally start journal transactions before acquiring quota I/O locks to preserve lock ordering.
- Mount cleanup labels are numerous; future edits must preserve reverse-order teardown or risk leaks/use-after-free around journals, sysfs, workqueues, timers, and group descriptors.
