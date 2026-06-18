# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_inode.c

Read completely: 261 lines.

Implements ULFS inode inactive/reclaim handling and block preallocation for LFS vnode writes.

Functions:
- `ulfs_inactive()` handles last-reference processing. It ignores stale-handle inodes with mode zero, removes extended attributes for unlinked inodes, truncates unlinked data to zero, decrements inode quota usage, clears mode/rdev on deleted inodes, marks inode state changed/updated, writes updates when dirty, and asks VFS to recycle mode-zero inodes.
- `ulfs_reclaim()` performs final vnode reclaim cleanup: calls `lfs_update()` twice with `UPDATE_CLOSE`, releases the device vnode, frees quota references, frees dirhash state when enabled, and returns the inode to a reusable state from the vnode layer's perspective.
- `ulfs_balloc_range()` allocates disk blocks over an offset/length range while holding affected VM pages busy, preventing stale disk contents from becoming visible to racing readers.

Allocation path:
- Computes the block-aligned allocation range and page range.
- Uses `VOP_GETPAGES()` with `PGO_NOBLOCKALLOC`, `PGO_PASTEOF`, and `PGO_GLOCKHELD` to obtain existing/new pages without allocating blocks first.
- Calls `GOP_ALLOC()` while pages are held.
- On success, clears `PG_RDONLY` for pages fully backed by new disk blocks and marks all pages dirty.
- Releases page busy state and frees the temporary page array.

Integration:
- Uses LFS update/truncate/allocation hooks, UVM page state, optional extended attributes, optional quotas, and optional directory hash cleanup.

Risks and notes:
- A comment questions whether two `lfs_update(... UPDATE_CLOSE)` calls in `ulfs_reclaim()` are really needed.
- `ulfs_balloc_range()` intentionally leaves pages around on allocation failure because they may already contain dirty data.
- Correctness depends on holding pages busy across allocation to avoid stale block exposure.
