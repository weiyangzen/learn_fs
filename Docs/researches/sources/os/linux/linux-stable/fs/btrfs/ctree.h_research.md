# File Research: sources/os/linux/linux-stable/fs/btrfs/ctree.h

## Purpose
Declares core Btrfs tree/path/root structures and public B-tree manipulation APIs used across the filesystem.

## Main Responsibilities
- Define B-tree path state and readahead modes.
- Define root state bits and the in-memory `struct btrfs_root`.
- Provide root accessors for flags, ids, log transaction ids, and generations.
- Define argument structures for extent replacement and extent dropping.
- Define leaf/node sizing helpers.
- Declare ctree search, COW, insert, delete, split, iteration, and lifecycle functions.
- Provide cleanup macros for automatic path freeing/release.

## Key Types
`struct btrfs_path` stores extent buffers, slots, lock modes, readahead mode, lowest search level, and flags controlling split searches, lock retention, skipped locking, commit-root search, extension search, nowait behavior, and error-release behavior.

`struct btrfs_root` stores current root node, commit root, log/reloc roots, root item/key, filesystem pointer, log synchronization state, dirty tracking, delalloc and ordered extent tracking, qgroup state, inode xarrays, defrag progress keys, and relocation/qgroup helper state.

Other important types include `struct btrfs_replace_extent_info`, `struct btrfs_drop_extents_args`, `struct btrfs_file_private`, and `struct btrfs_item_batch`.

## Important APIs
- Lifecycle: `btrfs_ctree_init()`, `btrfs_ctree_exit()`.
- Path lifecycle: `btrfs_alloc_path()`, `btrfs_release_path()`, `btrfs_free_path()`.
- Search/iteration: `btrfs_search_slot()`, `btrfs_search_old_slot()`, `btrfs_search_forward()`, `btrfs_find_next_key()`, `btrfs_next_old_leaf()`, `btrfs_next_old_item()`, `btrfs_previous_item()`, `btrfs_previous_extent_item()`.
- COW/root/block operations: `btrfs_root_node()`, `btrfs_read_node_slot()`, `btrfs_cow_block()`, `btrfs_force_cow_block()`, `btrfs_copy_root()`, `btrfs_block_can_be_shared()`.
- Item modification: `btrfs_set_item_key_safe()`, `btrfs_extend_item()`, `btrfs_truncate_item()`, `btrfs_split_item()`, `btrfs_duplicate_item()`, `btrfs_insert_item()`, `btrfs_insert_empty_items()`, `btrfs_del_items()`.

## Invariants And Notes
`search_commit_root` requires `skip_locking`. `need_commit_sem` pairs commit-root access with `commit_root_sem` protection. `nowait` search is intended for read-only paths. Shareable roots require special COW/backref handling, while non-shareable roots use simpler dirty-list tracking. `btrfs_for_each_slot` callers must preserve distinct handling for `0`, `1`, and negative errno.
