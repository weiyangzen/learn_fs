# File Research: sources/local-fs/f2fs-tools/fsck/quotaio_tree.c

Purpose: implements the quota qtree allocator, lookup, insertion, deletion, and scanning logic used by VFS v1 quota files.

Key behavior:
- Uses `QT_BLKSIZE` quota tree blocks and `struct qt_disk_dqdbheader` for data blocks.
- `qtree_entry_unused()` checks whether a disk quota entry is all zeros.
- `qtree_dqstr_in_blk()` computes entries per quota data block.
- Maintains free block and free-entry lists via `get_free_dqblk()`, `put_free_dqblk()`, `remove_free_dqentry()`, and `insert_free_dqentry()`.
- `find_free_dqentry()` locates or allocates a data block slot, increments block entry count, and records the dquot disk offset.
- `do_insert_tree()` recursively inserts qid-indexed references into a four-level tree.
- `qtree_write_dquot()` inserts a missing dquot into the tree if needed, converts memory to disk format, and writes the entry.
- `qtree_delete_dquot()` removes the tree reference and frees the data slot/block when usage and limits are all zero.
- `qtree_read_dquot()` finds an entry by ID, reads it, and converts it to memory format; absent entries return an empty dquot for the requested ID.
- `qtree_scan_dquots()` traverses all referenced blocks, calls a callback for nonempty entries, and records used entry/data-block counts.

Important dependencies:
- Uses `quota_handle` read/write callbacks from `quotaio.c`.
- Uses format-specific conversion and ID matching operations supplied by `quotaio_v2.c`.

Risk notes:
- Tree corruption is mostly logged and propagated as errors, but some helper writes ignore partial failure once list state has been logically changed.
- `find_block_dqentry()` logs when a referenced ID is absent but still returns a computed offset at the end of the block scan.
