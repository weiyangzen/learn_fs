# File Research: sources/local-fs/kdave-linux/fs/btrfs/disk-io.h

## Role

Internal header for Btrfs metadata I/O, root management, mount/unmount, superblock writing, log-tree creation, dirty metadata throttling, transaction cleanup, and free object ID allocation.

## Constants and Inline Helpers

- `BTRFS_SUPER_MIRROR_MAX` defines three possible superblock mirrors.
- `BTRFS_SUPER_MIRROR_SHIFT` controls backup superblock mirror spacing.
- `BTRFS_BDEV_BLOCKSIZE` fixes the block-device block size used for metadata/superblock reads at 4096 bytes.
- `btrfs_sb_offset()` maps mirror index 0 to `BTRFS_SUPER_INFO_OFFSET` and higher mirror indices to shifted 16 KiB offsets.
- `btrfs_grab_root()` safely increments a root refcount only if it is nonzero.

## API Surface

- Metadata I/O and validation: `read_tree_block()`, `btrfs_find_create_tree_block()`, `btrfs_validate_extent_buffer()`, `btrfs_buffer_uptodate()`, `btrfs_read_extent_buffer()`, `btree_csum_one_bio()`.
- Mount and superblock operations: `open_ctree()`, `close_ctree()`, `btrfs_start_pre_rw_mount()`, `btrfs_validate_super()`, `btrfs_check_features()`, `btrfs_check_super_csum()`, `write_all_supers()`, `btrfs_commit_super()`.
- Root operations: `btrfs_read_tree_root()`, `btrfs_insert_fs_root()`, `btrfs_free_fs_roots()`, `btrfs_get_fs_root()`, `btrfs_get_new_fs_root()`, `btrfs_get_fs_root_commit_root()`, `btrfs_global_root_insert()`, `btrfs_global_root_delete()`, `btrfs_global_root()`, `btrfs_csum_root()`, `btrfs_extent_root()`, `btrfs_put_root()`, `btrfs_drop_and_free_fs_root()`, `btrfs_create_tree()`.
- Log tree operations: `btrfs_alloc_log_tree_node()`, `btrfs_init_log_root_tree()`, `btrfs_add_log_tree()`.
- Lifecycle and cleanup: `btrfs_init_fs_info()`, `btrfs_free_fs_info()`, `btrfs_check_leaked_roots()`, `btrfs_cleanup_dirty_bgs()`, `btrfs_cleanup_one_transaction()`.
- Utility operations: `btrfs_mark_buffer_dirty()`, `btrfs_btree_balance_dirty()`, `btrfs_btree_balance_dirty_nodelay()`, `btrfs_get_num_tolerated_disk_barrier_failures()`, `btrfs_get_free_objectid()`, `btrfs_init_root_free_objectid()`.
- Test-only declaration: `btrfs_alloc_dummy_root()` under `CONFIG_BTRFS_FS_RUN_SANITY_TESTS`.

## Dependencies

Includes core Btrfs tree definitions, bio definitions, and ordered-data definitions. It forward declares common mount, root, device, transaction, superblock, extent-buffer, and parent-check structures to keep compile-time coupling lower for consumers.

## Research Notes

This header exposes the durable metadata lifecycle contract for the rest of Btrfs. The exported functions are broad because `disk-io.c` is the common implementation point for root lookup, tree-block validation, mount setup, unmount cleanup, and superblock commit behavior.
