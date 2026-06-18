# File Research: sources/local-fs/kdave-linux/fs/btrfs/free-space-tree.h

This header declares the free-space tree constants and API.

Key constants:
- `BTRFS_FREE_SPACE_BITMAP_SIZE` is the default size, in bytes, of new bitmap items.
- `BTRFS_FREE_SPACE_BITMAP_BITS` is the number of sectorsize units addressable by a default bitmap item.
- The comment notes that the last bitmap in a block group may be truncated and callers must not assume every existing bitmap has the default size.

Public API:
- Threshold setup: `btrfs_set_free_space_tree_thresholds()`.
- Lifecycle: `btrfs_create_free_space_tree()`, `btrfs_delete_free_space_tree()`, and `btrfs_rebuild_free_space_tree()`.
- Mount/cache loading: `btrfs_load_free_space_tree()`.
- Block group maintenance: `btrfs_add_block_group_free_space()` and `btrfs_remove_block_group_free_space()`.
- Range hooks: `btrfs_add_to_free_space_tree()` and `btrfs_remove_from_free_space_tree()`.
- Repair/cleanup: `btrfs_delete_orphan_free_space_entries()`.
- Lookup/root helpers: `btrfs_search_free_space_info()` and `btrfs_free_space_root()`.

Test-only API under `CONFIG_BTRFS_FS_RUN_SANITY_TESTS` exposes internal add/remove helpers, extent/bitmap conversion, and bitmap bit testing.
