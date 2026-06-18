# File Research: sources/os/linux/linux/fs/ext4/super.c

## Purpose
Implements ext4 superblock, mount, remount, unmount, journal, quota, error-reporting, lazy-init, statfs, and filesystem registration logic. This is the main VFS integration file for mounting ext4, and conditionally for ext2/ext3 compatibility.

## Main Elements
- Filesystem types and context operations: `ext4_fs_type`, optional `ext2_fs_type`, `ext3_fs_type`, `ext4_context_ops`, `ext4_init_fs_context()`, `ext4_get_tree()`, `ext4_reconfigure()`, `ext4_kill_sb()`.
- Buffer/superblock I/O helpers: `ext4_read_bh*()`, `ext4_sb_bread*()`, `ext4_sb_breadahead_unmovable()`, `ext4_load_super()`, `ext4_update_super()`, `ext4_commit_super()`.
- Metadata checksum helpers: `ext4_superblock_csum*()`, `ext4_group_desc_csum*()`, checksum seed setup, checksum journal trigger setup.
- Group descriptor accessors: block bitmap, inode bitmap, inode table, free inode/block counters, directory counts, itable-unused getters/setters.
- Error handling: `__ext4_error*()`, `__ext4_std_error()`, `ext4_handle_error()`, `save_error_info()`, `update_super_work()`, ratelimited warnings/messages, emergency read-only handling, journal abort propagation.
- Inode lifecycle: inode slab creation/destruction, `ext4_alloc_inode()`, `ext4_destroy_inode()`, `ext4_clear_inode()`, orphan-list debugging, NFS export inode lookup/metadata commit hooks.
- Mount option handling: `ext4_param_specs`, option token tables, `ext4_parse_param()`, `parse_options()`, superblock-stored option parsing, quota option reconciliation, dummy encryption checks, `ext4_apply_options()`, option display.
- Mount validation and setup: feature compatibility checks, geometry checks, block group descriptor loading, cluster/bigalloc checks, inode-size/time-range setup, casefold encoding init, journal data-mode checks, large folio constraints, DAX checks.
- Journal integration: internal/external journal open, journal bmap, journal load/recovery, checksum/fast-commit feature setup, commit callbacks, recovery completion, journal error clearing, freeze/unfreeze, sync.
- Lazy initialization: global `ext4lazyinit` thread, per-superblock lazy inode table and block bitmap prefetch requests, registration/unregistration, randomized scheduling.
- Capacity/accounting: overhead calculation, reserved cluster defaults, percpu counters, flex_bg summary initialization, statfs and project-quota-limited statfs.
- Quota support under `CONFIG_QUOTA`: quota operations, quotactl operations, system quota file enablement, journaled quota file flagging, quota read/write helpers.
- Module lifecycle: `ext4_init_fs()` initializes extents status, pending reservations, post-read processing, pageio, system zones, sysfs, mballoc, inode cache, fast-commit dentry cache, and registers filesystems; `ext4_exit_fs()` unwinds them.

## Control Flow
Initial mount enters `ext4_fill_super()`, allocates `ext4_sb_info`, normalizes the superblock id, selects the superblock block, then calls `__ext4_fill_super()`. That routine reads the on-disk superblock, verifies metadata checksums, establishes default options, parses superblock and user mount options, validates options/features/geometry, loads group descriptors, initializes journal or no-journal mode, builds xattr caches and overhead accounting, creates the reservation workqueue, reads the root inode, commits mount-state changes, initializes extents, percpu counters, mballoc, flex groups, lazy-init, orphan info, quotas, orphan cleanup, recovery completion, discard checks, error-report timers, ratelimits, and sysfs/proc registration.

Remount stores old options, applies the new context under writeback coordination, rejects unsupported data/journal/cache/delalloc changes, handles read-only transitions with sync/quota suspension/recovery flag cleanup, handles read-write transitions with feature and descriptor checksum checks, restarts MMP and quota as needed, updates system-zone and lazy-init state, and restores old options on failure.

Unmount unregisters sysfs/proc early, removes lazy-init and quotas, destroys workqueues and orphan info, tears down the journal or flushes superblock work, releases shrinkers/system-zone/mballoc/extents, commits clean state when possible, frees descriptors/flex groups/percpu counters/quota names/caches/MMP/DAX/encryption/encoding resources, invalidates block devices, and releases the superblock kobject.

## Dependencies And Integration
Depends heavily on Linux VFS, fs_context/fs_parser, block device APIs, buffer heads, jbd2, quota, fscrypt, fs-verity, Unicode casefolding, DAX, procfs/sysfs, percpu counters, workqueues, timers, and ext4 subsystems such as extents, mballoc, xattrs, fast commit, orphan handling, system zones, and fsmap. It exports core helpers used throughout ext4 for error reporting, metadata reads, descriptor accounting, sync, commit, and feature validation.

## Behavioral Notes
The file centralizes ext4’s safety gates: unsupported feature refusal, descriptor checksum validation, MMP protection, journal recovery requirements, journal/no-journal option compatibility, quota consistency, DAX restrictions, encryption/casefold requirements, and forced read-only behavior after serious errors. It writes superblock error state either through the journal or directly depending on journal state, and schedules deferred superblock updates to avoid unsafe lock ordering.

## Risk Notes
This file has a large blast radius. Bugs can lead to unsafe mounts, missed journal recovery, incorrect read-only/read-write transitions, stale or corrupt free-space accounting, orphan leakage, quota corruption, or lost error diagnostics. The most delicate areas are mount failure unwinding, remount rollback, journal recovery state transitions, group descriptor checksum handling, quota option changes, and direct versus journaled superblock writes.
