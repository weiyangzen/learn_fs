# File Research: sources/os/linux/linux-stable/fs/ubifs/recovery.c

## Summary
Implements UBIFS recovery from unclean unmounts, including master-node recovery, corrupted-tail LEB repair, read-only deferred cleanup, index/LPT head cleanup, GC-LEB recovery, and inode-size repair.

## Key APIs
- `ubifs_recover_master_node()`.
- `ubifs_write_rcvrd_mst_node()`.
- `ubifs_recover_leb()`.
- `ubifs_recover_log_leb()`.
- `ubifs_recover_inl_heads()`.
- `ubifs_clean_lebs()`.
- `ubifs_rcvry_gc_commit()`.
- `ubifs_recover_size_accum()`.
- `ubifs_recover_size()`.
- `ubifs_destroy_size_tree()`.

## Important Behavior
Recovery accepts corruption only when it matches UBIFS’s write model: nodes are written sequentially into erased LEBs, and power-cut corruption may affect only the last write unit with empty space afterward. Helpers such as `is_last_write()`, `no_more_nodes()`, `clean_buf()`, and `fix_unclean_leb()` enforce that model.

Master recovery reads both master LEBs, locates the last valid master node while allowing one interrupted write area, compares valid copies, and either writes a recovered master node immediately or stores it for later when mounted read-only. Recovered master writes set `UBIFS_MST_RCVRY` while writing, then restore flags in memory.

`ubifs_recover_leb()` scans a data/journal LEB, tolerates tail corruption only in valid recovery cases, drops incomplete grouped nodes, handles special GC-head min-IO-unit truncation, pads/cleans the rest of the LEB, and either writes the fixed LEB or records it on `unclean_leb_list` for later RW remount.

`ubifs_recover_log_leb()` can recover only the end of the log and verifies the next log LEB is empty or older than the current commit start sequence number.

GC recovery chooses or creates a valid `gc_lnum`, runs a commit so replay order is stable on future mounts, and may garbage-collect a dirty LEB into the GC head before unmapping the retained old GC LEB.

Size recovery accumulates inode sizes seen during journal replay. It removes data nodes for nonexistent inodes and fixes inode size upward either in place or by loading and journaling the inode, with read-only mounts pinning inodes until RW remount.

## Dependencies
Interacts with scan code, master code, journal replay, orphan recovery, TNC lookup/removal, inode journal writes, GC, lprops, write buffers, UBI LEB change/unmap, and authenticated node preparation.

## Risks
The power-cut corruption tests are intentionally strict; non-tail or non-empty-following corruption returns `-EUCLEAN`. Read-only mounts defer required media writes, so remount paths must call cleanup. GC recovery ordering is delicate because committing before/after GC changes how subsequent mounts see orphan and GC operations.
