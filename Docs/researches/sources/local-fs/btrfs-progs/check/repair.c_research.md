# File Research: sources/local-fs/btrfs-progs/check/repair.c

## Purpose
Provides shared repair helpers for `btrfs check`, including unsafe key updates, corrupt extent-root block tracking, used-block reconstruction, block accounting fixup, orphan device-extent removal, and tree-checker repair integration.

## Main Functions
- `btrfs_fixup_low_keys()` updates ancestor node separator keys after modifying a low-level key, stopping once the changed slot is not zero.
- `btrfs_set_item_key_unsafe()` rewrites a leaf item key and fixes low keys upward; it is explicitly intended for fsck repair paths.
- `btrfs_add_corrupt_extent_record()` records corrupt extent-tree blocks in `fs_info->corrupt_blocks` using a cache extent keyed by start/length plus first key and level.
- `btrfs_mark_used_tree_blocks()` traverses chunk, root, and block-group trees to mark tree blocks as used or pin them.
- `btrfs_mark_used_blocks()` populates an extent_io_tree from extent roots and the remap tree.
- `btrfs_fix_block_accounting()` rebuilds block-group `used` and `space_info->bytes_used` from actual used extents, updates dirty block groups, and rewrites super `bytes_used`.
- `btrfs_remove_dev_extent()` deletes one dev-extent item, subtracts its length from the device's bytes-used counter, updates the device item, and commits.
- `btrfs_check_block_for_repair()` runs leaf/node tree checker logic and records corrupt extent-tree blocks for repair handling.

## Traversal Details
`traverse_tree_blocks()` recursively walks tree nodes. For level-1 non-root nodes, it can mark children directly without reading leaves, while root tree traversal follows root items into other tree roots. Already marked ranges are skipped to avoid loops on damaged filesystems.

## Error Handling
Errors are returned as negative errno-style values for internal helpers and nonzero repair failures. Transaction paths abort on mutation failures and commit on success. Device extent removal reports missing devices, search failure, deletion failure, underflow-like `bytes_used` cases, and commit errors.

## Dependencies
Uses ctree accessors, transactions, extent IO trees, disk IO, volumes, extent cache, messages, and tree checker internals.
