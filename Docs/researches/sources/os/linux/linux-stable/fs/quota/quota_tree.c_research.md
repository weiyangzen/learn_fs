# File Research: sources/os/linux/linux-stable/fs/quota/quota_tree.c

## Purpose
Implements the shared on-disk quota trie used by VFS quota v2 formats. It manages lookup, insertion, deletion, iteration, and free-space tracking for quota records stored in fixed-size quota blocks.

## Data Model
The quota file is a radix tree:
- Internal tree blocks contain little-endian block references.
- Leaf/data blocks contain a `qt_disk_dqdbheader` followed by fixed-size quota entries.
- `QT_TREEOFF` identifies the root tree block offset.
- `qtree_mem_dqinfo` supplies block size, depth, record size, type, and format-specific callbacks.

## Main Responsibilities
- Block I/O wrappers: `read_blk()` and `write_blk()`.
- Sanity checks for free-list pointers and entry counts.
- Empty block free-list management via `get_free_dqblk()` and `put_free_dqblk()`.
- Data block free-entry list management via `insert_free_dqentry()` and `remove_free_dqentry()`.
- Record insertion through `dq_insert_tree()` and recursive `do_insert_tree()`.
- Record deletion through `qtree_delete_dquot()` and recursive `remove_tree()`.
- Lookup through `find_dqentry()`, `find_tree_dqentry()`, and `find_block_dqentry()`.
- Iteration through `qtree_get_next_id()`.

## Exported API
- `qtree_entry_unused()`
- `qtree_write_dquot()`
- `qtree_delete_dquot()`
- `qtree_read_dquot()`
- `qtree_release_dquot()`
- `qtree_get_next_id()`

## Corruption Defenses
The implementation checks:
- block number ranges,
- free-list header ranges,
- tree cycles,
- insertion into already-present entries,
- missing referenced quota IDs,
- excessive tree depth.

Errors are reported with `quota_error()` and generally return `-EIO` or `-EUCLEAN`.
