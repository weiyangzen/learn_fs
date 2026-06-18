# File Research: sources/os/linux/linux/fs/btrfs/free-space-tree.h

## Purpose
Declares the public interface and constants for Btrfs free-space tree management.

## Constants
- `BTRFS_FREE_SPACE_BITMAP_SIZE = 256`: default bitmap item payload size in bytes.
- `BTRFS_FREE_SPACE_BITMAP_BITS`: number of sectors represented by that bitmap payload.

## Public API
- Tree lifecycle:
  - `btrfs_create_free_space_tree()`
  - `btrfs_delete_free_space_tree()`
  - `btrfs_rebuild_free_space_tree()`
- Block-group setup/removal:
  - `btrfs_add_block_group_free_space()`
  - `btrfs_remove_block_group_free_space()`
  - `btrfs_set_free_space_tree_thresholds()`
- Incremental updates:
  - `btrfs_add_to_free_space_tree()`
  - `btrfs_remove_from_free_space_tree()`
- Loading and lookup:
  - `btrfs_load_free_space_tree()`
  - `btrfs_search_free_space_info()`
  - `btrfs_free_space_root()`
- Cleanup:
  - `btrfs_delete_orphan_free_space_entries()`

## Test Exports
When sanity tests are enabled, the header exposes internal add/remove and conversion helpers plus `btrfs_free_space_test_bit()`.

## Design Notes
This header is intentionally smaller than `free-space-cache.h`; it exposes only the persistent free-space tree API and hides most bitmap/extent mutation internals in `free-space-tree.c`.
