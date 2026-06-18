# File Research: sources/os/linux/linux-stable/fs/nilfs2/inode.c

## Summary
Implements NILFS inode operations, block mapping for VFS I/O, inode creation/loading/eviction, B-tree node cache inode management, dirty inode/file tracking, truncation, setattr/permission, and fiemap.

## Main Responsibilities
- Maps file logical blocks through NILFS bmaps and DAT.
- Handles buffered read, readahead, write begin/end, dirty folios, writepages, and read-only direct I/O.
- Allocates and initializes new inodes.
- Reads on-disk inodes from ifile and assigns VFS operations.
- Maintains inode-cache identity by root, checkpoint, and special inode type.
- Attaches/detaches associated B-tree node cache inodes and shadow inodes.
- Serializes inode data back to raw NILFS inode records.
- Truncates bmaps and evicts deleted inodes.
- Tracks dirty files for segment construction.
- Implements setattr, snapshot write permission checks, and fiemap reporting.

## Important Behavior
`nilfs_get_block()` first performs contiguous bmap lookup under the DAT metadata semaphore. On a hole with `create`, it starts a NILFS transaction, inserts a delayed block into the bmap, marks the inode dirty synchronously, commits, and returns a mapped delayed/new buffer with block number 0.

Writeback does not directly write pages except for sync mode, where it constructs a data-sync segment. Dirty folio handling marks only mapped buffers dirty and increments the filesystem dirty-block counter through `nilfs_set_file_dirty()`.

New inode creation allocates an ifile entry, initializes ownership/timestamps/flags/generation, reads an empty bmap for regular directories/symlinks, inserts the inode using an iget test keyed by NILFS root and type, and initializes ACLs.

Normal inode lookup uses `iget5_locked()` with `nilfs_iget_args`. GC, B-tree-node-cache, and shadow inodes share inode numbers with their owning inodes but differ by `i_type`, root, and checkpoint. Associated B-tree node cache inodes share the owner's bmap and store node pages separately from data pages.

Eviction truncates page cache, avoids writes when read-only or writer-detached, truncates bmap blocks for deleted normal inodes, deletes the ifile record, updates root inode count, clears metadata state, and detaches associated node cache inodes.

Dirty tracking puts inodes on `ns_dirty_files` with `NILFS_I_QUEUED`, uses `NILFS_I_DIRTY`/`NILFS_I_BUSY`, and holds an inode reference while queued. `__nilfs_mark_inode_dirty()` reloads the ifile block if needed, updates the raw inode, marks buffers dirty, and marks the ifile metadata dirty.

`nilfs_fiemap()` merges physical contiguous extents from bmap lookup and reports delayed-allocation extents from NILFS uncommitted extent tracking.

## Risks
The inode cache intentionally creates multiple in-memory inodes with the same inode number for normal, GC, B-tree-node-cache, and shadow roles; the type/root/checkpoint key must be honored everywhere. Dirty inode queueing depends on reference acquisition and state bits under `ns_inode_lock`. Truncation and eviction have limited error reporting because VFS callbacks often cannot return failures.
