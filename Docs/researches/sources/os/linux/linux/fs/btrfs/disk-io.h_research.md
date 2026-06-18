# File Research: sources/os/linux/linux/fs/btrfs/disk-io.h

## Purpose

`disk-io.h` declares the public interface for Btrfs disk/tree I/O, root management, mount/open/close lifecycle, superblock validation/writing, metadata buffer validation, log tree allocation, transaction cleanup, and object-id allocation.

## Important Constants

- `BTRFS_SUPER_MIRROR_MAX`: three superblock mirror locations.
- `BTRFS_SUPER_MIRROR_SHIFT`: shift used to derive backup superblock offsets.
- `BTRFS_BDEV_BLOCKSIZE`: fixed 4096-byte block size used for specific metadata reads like superblocks.
- `btrfs_sb_offset()`: inline helper returning primary or backup superblock offsets.

## Main API Groups

Mount and filesystem lifecycle:

- `btrfs_init_fs_info()`
- `open_ctree()`
- `close_ctree()`
- `btrfs_start_pre_rw_mount()`
- `btrfs_free_fs_info()`

Superblock and feature handling:

- `btrfs_check_super_csum()`
- `btrfs_validate_super()`
- `btrfs_check_features()`
- `write_all_supers()`
- `btrfs_commit_super()`
- `btrfs_get_num_tolerated_disk_barrier_failures()`

Tree block I/O:

- `read_tree_block()`
- `btrfs_find_create_tree_block()`
- `btrfs_validate_extent_buffer()`
- `btrfs_buffer_uptodate()`
- `btrfs_read_extent_buffer()`
- `btree_csum_one_bio()`
- `btrfs_mark_buffer_dirty()`

Root management:

- `btrfs_read_tree_root()`
- `btrfs_insert_fs_root()`
- `btrfs_free_fs_roots()`
- `btrfs_get_fs_root()`
- `btrfs_get_new_fs_root()`
- `btrfs_get_fs_root_commit_root()`
- `btrfs_global_root_insert()`
- `btrfs_global_root_delete()`
- `btrfs_global_root()`
- `btrfs_csum_root()`
- `btrfs_extent_root()`
- `btrfs_drop_and_free_fs_root()`
- `btrfs_put_root()`
- `btrfs_create_tree()`

Log tree and transaction cleanup:

- `btrfs_alloc_log_tree_node()`
- `btrfs_init_log_root_tree()`
- `btrfs_add_log_tree()`
- `btrfs_cleanup_dirty_bgs()`
- `btrfs_cleanup_one_transaction()`

Object-id helpers:

- `btrfs_get_free_objectid()`
- `btrfs_init_root_free_objectid()`

## Inline Helper

`btrfs_grab_root()` conditionally increments a root reference if the root is non-null and not already at zero, protecting callers from use-after-free when retrieving roots from shared structures.

## Integration Points

This header is included by Btrfs mount code, export code, transaction code, root-tree users, metadata I/O paths, and test infrastructure.

## Invariants

- Superblock offsets are fixed and must not be changed.
- `btrfs_grab_root()` does not guarantee the tree is not being dropped; it only protects the root structure lifetime.
- Callers must pair grabbed/read roots with `btrfs_put_root()`.
