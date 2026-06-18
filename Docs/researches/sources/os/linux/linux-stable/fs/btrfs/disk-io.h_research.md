# File Research: sources/os/linux/linux-stable/fs/btrfs/disk-io.h

## Purpose
Public declarations for Btrfs disk IO, mount/unmount, root lookup/lifetime, metadata buffer validation, log tree setup, transaction cleanup, superblock writes, and objectid allocation.

## Constants And Inline Helpers
- `BTRFS_SUPER_MIRROR_MAX`: three superblock mirrors.
- `BTRFS_SUPER_MIRROR_SHIFT`: shift used for backup superblock offsets.
- `BTRFS_BDEV_BLOCKSIZE`: fixed 4096-byte block size for superblock-style metadata reads.
- `btrfs_sb_offset()` maps mirror index to its logical superblock location.

## Declared Interfaces
- Mount lifecycle: `open_ctree()`, `close_ctree()`, `btrfs_start_pre_rw_mount()`.
- Superblock handling: `btrfs_check_super_csum()`, `btrfs_validate_super()`, `btrfs_check_features()`, `write_all_supers()`, `btrfs_commit_super()`.
- Root management: `btrfs_read_tree_root()`, `btrfs_insert_fs_root()`, `btrfs_free_fs_roots()`, `btrfs_get_fs_root()`, `btrfs_get_new_fs_root()`, `btrfs_get_fs_root_commit_root()`, global root insert/delete/lookup, csum/extent-root selectors, `btrfs_drop_and_free_fs_root()`, `btrfs_put_root()`.
- Metadata buffers: `read_tree_block()`, `btrfs_find_create_tree_block()`, `btrfs_validate_extent_buffer()`, `btrfs_buffer_uptodate()`, `btrfs_read_extent_buffer()`, `btree_csum_one_bio()`, `btrfs_mark_buffer_dirty()`.
- Log trees: `btrfs_alloc_log_tree_node()`, `btrfs_init_log_root_tree()`, `btrfs_add_log_tree()`.
- Cleanup: `btrfs_cleanup_dirty_bgs()`, `btrfs_cleanup_one_transaction()`.
- Miscellaneous: dirty metadata throttling, tolerated barrier failures, free objectid initialization/allocation.

## Inline Lifetime Helper
`btrfs_grab_root()` safely increments a root refcount only if non-zero, allowing lookup paths to avoid racing with root teardown.

## Compile-Time Conditional
`btrfs_alloc_dummy_root()` is declared only under `CONFIG_BTRFS_FS_RUN_SANITY_TESTS`.
