# File Research: sources/os/linux/linux/fs/quota/quota_tree.c

Quota-file radix tree support for VFS quota v2 formats. It manages the tree of ID-to-dquot-entry mappings, free block lists, free-entry lists, quota entry insertion/removal, lookup, read/write, and next-ID enumeration.

Key responsibilities:
- Computes per-level indexes for quota IDs with `__get_index()` / `get_index()`.
- Reads and writes quota blocks with `read_blk()` and `write_blk()`.
- Validates block headers and block-number ranges with `check_dquot_block_header()` and `do_check_range()`.
- Manages free empty blocks:
  - `get_free_dqblk()`
  - `put_free_dqblk()`
- Manages blocks that contain free entries:
  - `remove_free_dqentry()`
  - `insert_free_dqentry()`
- Detects unused disk entries with exported `qtree_entry_unused()`.
- Finds a free dquot slot with `find_free_dqentry()`.
- Inserts quota entries into the tree via `dq_insert_tree()` / `do_insert_tree()`.
- Writes an in-memory dquot to disk with exported `qtree_write_dquot()`.
- Frees/removes quota entries with `free_dqentry()`, `remove_tree()`, and exported `qtree_delete_dquot()`.
- Looks up quota entries with `find_dqentry()` / `find_tree_dqentry()` / `find_block_dqentry()`.
- Reads quota entries into memory with exported `qtree_read_dquot()`.
- Releases fake unused dquots with exported `qtree_release_dquot()`.
- Enumerates next quota IDs with exported `qtree_get_next_id()`.

On-disk model:
- Block `QT_TREEOFF` is the tree root.
- Internal tree blocks store little-endian block references.
- Leaf/data blocks begin with `struct qt_disk_dqdbheader`, followed by fixed-size format-specific dquot entries.
- `dqi_free_blk` tracks fully free blocks.
- `dqi_free_entry` tracks blocks that still have at least one free dquot entry.

Safety checks:
- `MAX_QTREE_DEPTH` limits recursion.
- Range checks reject corrupt block references.
- Cycle checks detect quota-tree loops.
- Header checks validate free-list links and entry counts.
- Paranoia checks reject duplicate insertions and impossible full-block states.

Research notes:
- Format-specific conversion is delegated through `struct qtree_fmt_operations`, supplied by `quota_v2.c`.
- This file is generic tree mechanics; it does not define the v2 disk dquot payload fields.
