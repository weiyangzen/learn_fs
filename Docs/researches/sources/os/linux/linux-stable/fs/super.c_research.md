# File Research: sources/os/linux/linux-stable/fs/super.c

Purpose: Implements core VFS superblock lifecycle, lookup/reuse, mount tree acquisition, shutdown, block-device superblock integration, remount/reconfigure handling, filesystem iteration, freeze/thaw, emergency operations, anonymous device allocation, and per-superblock cache shrinking.

Key responsibilities:
- Maintains global superblock lists and per-filesystem `fs_supers` membership under `sb_lock`.
- Allocates and initializes `struct super_block`, including shrinkers, LRUs, freeze semaphores, namespace state, security state, backing-dev defaults, and lockdep classes.
- Provides active and temporary superblock reference management through `s_active`, `s_count`, `deactivate_super()`, `deactivate_locked_super()`, `put_super()`, and `grab_super()`.
- Publishes superblocks via `sget_fc()` and legacy `sget()`, including namespace compatibility and exclusive mount checks.
- Implements `generic_shutdown_super()`, `kill_anon_super()`, and `kill_block_super()` cleanup paths.
- Provides `get_tree_nodev()`, `get_tree_single()`, `get_tree_keyed()`, `get_tree_bdev_flags()`, `get_tree_bdev()`, and `vfs_get_tree()` helpers for filesystem mount setup.
- Handles block-device ownership callbacks through `fs_holder_ops`: mark-dead, sync, freeze, and thaw.
- Implements `reconfigure_super()` for remount flag changes, read-only transitions, security remount checks, and filesystem-specific reconfigure callbacks.
- Implements emergency remount, emergency thaw, system-wide freeze/thaw, and direct-IO completion workqueue creation.
- Implements `freeze_super()` and `thaw_super()` state transitions across write, pagefault, internal-FS, and complete freeze levels.

Important interactions:
- Calls into filesystem `super_operations`, fs_context callbacks, security hooks, fscrypt cleanup, fsnotify, cgroup writeback, writeback/sync, block layer, bdi, shrinker, and dcache/inode eviction code.
- `super_wake()` and `super_lock()` coordinate `SB_BORN`, `SB_DYING`, and `SB_DEAD` visibility for concurrent mount/shutdown paths.
- Block-device mounting uses `lookup_bdev()`, `bdev_file_open_by_dev()`, freeze-count checks, and holder callbacks.
- Freeze/thaw depends on `s_writers` counters and may distinguish userspace, kernel, nested block-device, and exclusive kernel freeze owners.

Notable invariants and risks:
- Newly allocated superblocks are published before `SB_BORN`; walkers must wait for born or dying state.
- `s_umount` ordering and `sb_start_write()` ordering drive the careful unlock/relock behavior in freeze and remount paths.
- Reusing superblocks across user namespaces is rejected unless allowed by the filesystem context.
- Freeze counts and owner semantics are subtle: all freeze holders share one active reference, and thaw only fully unlocks when both kernel and userspace counts reach zero.
- Shutdown poisons busy inodes after unmount corruption detection to make later misuse fail loudly.
