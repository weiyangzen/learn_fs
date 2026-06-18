# File Research: sources/os/linux/linux-stable/fs/btrfs/tree-checker.h

## Role

Header for Btrfs tree block validation.

## Key Types

- `struct btrfs_tree_parent_check`: caller-provided expectations for tree-block verification:
  - `owner_root`: expected owner root, zero to skip.
  - `transid`: expected transaction id, zero only for limited contexts such as backref walking.
  - `first_key` plus `has_first_key`: expected first key from parent.
  - `level`: expected tree level.
- `enum btrfs_tree_block_status`: internal detailed validation results, including invalid item count, parent key, key order, level, free space, offsets, block pointer, item, owner, and missing `WRITTEN` flag.

## Constants

- `BTRFS_BLOCK_GROUP_VALID`: accepted block-group type/profile/remap flag mask for chunk validation.

## Exported API

- `__btrfs_check_leaf()` and `__btrfs_check_node()`: detailed status-code validators, exported for btrfs-progs compatibility.
- `btrfs_check_leaf()` and `btrfs_check_node()`: kernel errno wrappers.
- `btrfs_check_chunk_valid()`: common chunk validator for leaf chunk items and superblock system chunk array.
- `btrfs_check_eb_owner()`: owner-root validator.
- `btrfs_verify_level_key()`: parent-level and first-key verification helper.
