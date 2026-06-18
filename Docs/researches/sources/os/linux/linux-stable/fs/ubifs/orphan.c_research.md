# File Research: sources/os/linux/linux-stable/fs/ubifs/orphan.c

## Summary
Manages UBIFS orphan inode tracking across normal operation, commits, unclean-mount recovery, and debug validation.

## Key APIs
- `ubifs_add_orphan()`.
- `ubifs_delete_orphan()`.
- `ubifs_orphan_start_commit()`.
- `ubifs_orphan_end_commit()`.
- `ubifs_clear_orphans()`.
- `ubifs_mount_orphans()`.

## Important Behavior
An orphan is an inode whose committed inode node has link count zero, typically an unlinked but still-open file. The in-memory orphan set is stored in an rb-tree plus ordered lists. New orphans also live on `orph_new`; committing orphans are linked by `cnext`; orphans deleted while being committed are moved to a delayed deletion chain.

`ubifs_add_orphan()` enforces `max_orphans`, rejects duplicate inode numbers, and tracks total/new counts under `orphan_lock`. `ubifs_orphan_start_commit()` freezes current new orphans into the commit list, resets the new list, and sets the master no-orphans flag state. `ubifs_orphan_end_commit()` writes pending orphan nodes if needed, then erases delayed deletions and runs debug validation.

Orphan nodes are appended to the fixed orphan area. If the remaining half-area budget is insufficient, `consolidate()` rewrites all non-new orphans atomically from the start of the orphan area and unmaps unused LEBs.

Mount recovery uses `kill_orphans()` to scan orphan LEBs, recover torn orphan LEBs when needed, and call `ubifs_tnc_remove_ino()` for orphaned inodes whose current inode node still has `nlink == 0`. Commit numbers and the high “last node for commit” bit distinguish current orphan records from stale ones.

## Dependencies
Uses rbtrees/lists, `orphan_lock`, scan/recovery helpers, TNC lookup/removal, orphan-area geometry, UBIFS node writing, and debug index walking.

## Risks
The orphan area is fixed-size, so `max_orphans` validation is part of correctness. Commit-time delayed deletion prevents freeing objects still on the commit list. Recovery deliberately avoids deleting O_TMPFILE-style reborn inodes by rechecking `nlink`.
