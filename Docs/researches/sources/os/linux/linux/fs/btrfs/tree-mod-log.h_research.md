# File Research: sources/os/linux/linux/fs/btrfs/tree-mod-log.h

## Purpose

`tree-mod-log.h` declares the public interface for Btrfs' in-memory tree modification log. It is included by code that either records tree mutations or requests historical views of tree blocks.

## Public Types

`struct btrfs_seq_list` represents one active tree mod log user. It contains a list node for `fs_info->tree_mod_seq_list` and the user's sequence number.

`BTRFS_SEQ_LIST_INIT()` initializes a static or stack sequence-list object with an empty list and zero sequence. `BTRFS_SEQ_LAST` is the maximum `u64`, used as the cleanup threshold when no older user remains.

`enum btrfs_mod_log_op` lists every operation that `tree-mod-log.c` can record:

- key replace, add, and remove.
- key removal while freeing a block.
- key removal while moving slots.
- key movement within a node.
- root replacement.

## Public API

The header exposes sequence lifetime helpers:

- `btrfs_get_tree_mod_seq()`
- `btrfs_put_tree_mod_seq()`
- `btrfs_tree_mod_log_lowest_seq()`

It exposes logging hooks for tree modification sites:

- `btrfs_tree_mod_log_insert_root()`
- `btrfs_tree_mod_log_insert_key()`
- `btrfs_tree_mod_log_free_eb()`
- `btrfs_tree_mod_log_eb_copy()`
- `btrfs_tree_mod_log_insert_move()`

It exposes historical read helpers:

- `btrfs_tree_mod_log_rewind()`
- `btrfs_get_old_root()`
- `btrfs_old_root_level()`

## Filesystem Role

The header is the contract between Btrfs tree modification code and readers that need stable old metadata. It intentionally keeps the private rb-tree record format hidden in `tree-mod-log.c`.
