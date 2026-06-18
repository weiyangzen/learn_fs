# File Research: sources/local-fs/kdave-linux/fs/btrfs/fs.h

This header is a central Btrfs filesystem-wide declaration point. It defines size constants, runtime state bits, mount option bits, supported feature masks, core filesystem state structures, checksum context APIs, exclusive operation APIs, and many small filesystem helpers.

Constants and feature masks:
- Defines Btrfs block size limits, max extent size, trim length limit, superblock location/size, metadata reservation helpers, format strings, unlink metadata unit count, and reserved device range.
- `BTRFS_FEATURE_COMPAT_RO_SUPP` includes free-space tree, verity, and block group tree support.
- `BTRFS_FEATURE_INCOMPAT_SUPP_STABLE` lists stable incompat features such as mixed backrefs, mixed groups, RAID56, extended irefs, no-holes, metadata UUID, zoned mode, and simple quota.
- Experimental builds add RAID stripe tree, extent tree v2, and remap tree support.
- Mount flags include cache/discard options, free-space tree, no-space-cache, log replay controls, checksum ignore options, reference tracking, and other mount behavior.

Runtime state:
- `BTRFS_FS_STATE_*` bits track remounting, read-only state, transaction abort reporting, log replay failure, device replacement blocking, dummy test fs, checksum ignore modes, log cleanup error, delayed iput shutdown, and emergency shutdown.
- `BTRFS_FS_*` flag bits track closing/open state, quota, free-space tree creation/untrusted state, cleaner/discard/relocation/balance activity, v1 space-cache cleanup, transaction commit requests, unfinished drops, active zone tracking, feature changes, and 32-bit warnings.

Important structures:
- `struct btrfs_dev_replace` stores device replace state, cursors, error counters, source/target devices, locks, scrub progress, and wait/task state.
- `struct btrfs_free_cluster` represents allocator clusters used by metadata allocations and SSD-spread data allocations.
- `struct btrfs_discard_ctl` owns async discard work, discard lists, throttling parameters, current block group, filter sizes, and discard statistics.
- `enum btrfs_exclusive_operation` enumerates mutually exclusive device/balance/resize/swap operations.
- `struct btrfs_commit_stats` tracks commit counts and durations for sysfs.
- `struct btrfs_delayed_root` tracks delayed inode/item work.
- `struct btrfs_fs_info` is the central mounted-filesystem object, holding global roots, block group cache, mapping tree, reservations, generation counters, mount options, transactions, locks, worker pools, discard control, qgroups, extent buffer cache, device replace state, reclaim lists, block sizes, zoned state, active block groups, commit stats, and debug state.

Free-space related fields in `struct btrfs_fs_info`:
- `block_group_cache_tree` and `block_group_cache_lock` store mounted block groups.
- `excluded_extents` tracks ranges excluded from allocation/cache loading, such as log tree blocks or super stripes.
- `ro_block_group_mutex` coordinates block group read-only transitions with free-space cache allocation/writeout.
- `caching_block_groups` and `caching_workers` support asynchronous free-space cache loading.
- `data_alloc_cluster` and `meta_alloc_cluster` hold allocator clusters populated by free-space-cache code.
- `discard_ctl` coordinates async discard lists and accounting.
- `unused_bgs`, `fully_remapped_bgs`, and reclaim-related locks/work items connect free-space/discard state to block group deletion and reclaim.

Inline helpers and macros:
- `_Generic` helpers map folios/inodes to `btrfs_inode` or `btrfs_fs_info`.
- `btrfs_alloc_write_mask()` removes `__GFP_FS` from mapping allocation masks to avoid filesystem recursion.
- Generation helpers use `READ_ONCE()`/`WRITE_ONCE()` for current, committed, and root-drop generations.
- Metadata sizing helpers estimate tree COW/insert reservation needs from nodesize and tree height.
- `btrfs_is_zoned()` gates zoned logic on config and `fs_info->zone_size`.
- `count_max_extents()` counts filesystem max-extent chunks, with a sanity-test fallback for null fs_info.
- Feature and mount option macros wrap superblock flag reads/writes and mount option bit operations.
- Closing, cleaner sleep, unfinished-drop wakeup, shutdown, ordered folio, and test-mode helpers centralize common checks.

Declared functions:
- Checksum metadata and streaming checksum functions.
- Exclusive operation start/finish/balance helpers.
- IOCTL path validation.
- Feature flag set/clear implementations.
- Test-only inode destroy hook under `CONFIG_BTRFS_FS_RUN_SANITY_TESTS`.

This header is included throughout Btrfs and forms the shared context needed by the free-space cache/tree files in this group.
