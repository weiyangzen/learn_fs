# File Research: sources/os/linux/linux/fs/ubifs/orphan.c

## Role

Tracks UBIFS orphan inodes, writes orphan records during commit, deletes recorded orphan inodes after unclean unmounts, clears orphan areas after clean mounts, and provides debug consistency checks.

## Key APIs

- `ubifs_add_orphan()`
- `ubifs_delete_orphan()`
- `ubifs_orphan_start_commit()`
- `ubifs_orphan_end_commit()`
- `ubifs_clear_orphans()`
- `ubifs_mount_orphans()`

## Important Behavior

An orphan is an inode committed with link count zero, commonly an unlinked but still-open file. UBIFS keeps current orphans in an rb-tree plus ordered lists. `ubifs_add_orphan()` inserts a new orphan, enforces `max_orphans`, and tracks it on both the all-orphans and new-orphans lists. `ubifs_delete_orphan()` removes an orphan immediately unless it is currently being committed, in which case it is marked for delayed deletion.

Commit starts by moving all new orphans to a cnext commit list and marking whether the master node should advertise no-orphans. Commit end writes pending orphan nodes if needed, then erases delayed-deletion orphan objects.

Orphan nodes are written sequentially through the fixed orphan area. If available tail space is insufficient, `consolidate()` rewrites all non-new orphans atomically from the first orphan LEB, leaving half the total orphan area available for future additions. The last orphan node for a commit sets the high bit of `cmt_no`.

On mount after an unclean unmount, `kill_orphans()` scans orphan LEBs, recovers corrupt orphan LEBs if needed, honors commit-number ordering and last-node markers, and removes keys for recorded orphan inodes from the TNC when the inode still has `nlink == 0`. This protects relinked `O_TMPFILE` cases.

`ubifs_mount_orphans()` sets `max_orphans`, allocates the orphan buffer for writable mounts, kills orphans after unclean mounts, or clears the orphan area after clean writable mounts.

Debug code scans both the orphan area and the index to verify that zero-link inode nodes are represented either on flash or in the in-memory orphan tree.

## Dependencies

Uses rbtrees, spinlocks, UBIFS scan/recovery, TNC lookup/removal, node write/change/unmap helpers, orphan node format, and debug index walking.

## Research Notes

The orphan write protocol is crash-order sensitive. Consolidation is designed so an unclean unmount cannot lose orphan records. Deletion during commit is deferred to avoid freeing objects still referenced by the commit list.
