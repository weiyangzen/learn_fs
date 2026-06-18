# File Research: sources/os/linux/linux/fs/super.c

Purpose: Core VFS superblock management: allocation, lookup/reuse, reference lifetimes, shutdown, mount tree construction helpers, block-device-backed superblocks, freeze/thaw, emergency remount/thaw, and per-superblock backing device setup.

Key APIs and entry points:
- Exports lifecycle helpers: `deactivate_locked_super`, `deactivate_super`, `retire_super`, `generic_shutdown_super`, `put_super`, `drop_super`, `drop_super_exclusive`.
- Exports lookup/mount helpers: `sget_fc`, `sget_dev`, `get_tree_nodev`, `get_tree_single`, `get_tree_keyed`, `get_tree_bdev_flags`, `get_tree_bdev`, `vfs_get_tree`.
- Exports block/anonymous helpers: `get_anon_bdev`, `free_anon_bdev`, `set_anon_super`, `kill_anon_super`, `setup_bdev_super`, `kill_block_super`, `fs_holder_ops`.
- Exports freeze APIs: `freeze_super`, `thaw_super`, plus `filesystems_freeze`, `filesystems_thaw`, `emergency_thaw_all`.
- Exports BDI/workqueue setup: `super_setup_bdi_name`, `super_setup_bdi`, `sb_init_dio_done_wq`.

Implementation notes:
- Maintains global `super_blocks` under `sb_lock`; individual lifecycle transitions use `s_umount`, `s_count`, `s_active`, and flags including `SB_BORN`, `SB_DYING`, `SB_DEAD`, `SB_ACTIVE`.
- `alloc_super()` initializes locks, lists, shrinker state, writeback/error state, freeze/writer counters, LRU structures, and namespace ownership.
- `generic_shutdown_super()` performs the main teardown sequence: mark dying, shrink/evict dentries and inodes, call filesystem shutdown hooks, unregister shrinkers, clean BDI, and release bdev/anode resources.
- `sget_fc()` implements the central find-or-create path for fs_context-based mounts, handling test/set callbacks, user namespace choice, active references, and races with existing superblocks.
- Block-device path coordinates `blkdev_get_by_path`, holder ops, block size, `SB_RDONLY`, `FMODE_EXCL`, bdev sync, freeze, thaw, and surprise removal marking.
- Freeze logic supports userspace and kernel holders, nesting rules, exclusive/nonexclusive owners, partial-freeze waiting, lockdep annotations, and staged writer exclusion.

Concurrency and correctness:
- Heavy use of `sb_lock`, `s_umount`, per-super wait queues, percpu rwsems for write levels, and memory ordering around no-space/lifecycle flags.
- `super_lock()` can return false if a superblock is not born or has begun dying/dead transition.
- Freeze/thaw state is intentionally guarded by `s_umount`; writer exclusion proceeds through freeze levels before filesystem `->freeze_fs`.
- Block holder callbacks must avoid racing bdev removal with superblock teardown.

Dependencies:
- VFS fs_context/mount API, block layer holder API, writeback/BDI, shrinker, quota, security, lockdep, IDA anonymous devices.
