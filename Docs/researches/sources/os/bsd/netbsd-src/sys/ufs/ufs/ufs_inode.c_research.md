# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_inode.c

This file implements shared UFS inode lifecycle and allocation/truncation support.

Key responsibilities:
- `ufs_inactive` handles last-reference cleanup, deletion of unlinked inodes, truncation of all data, quota inode decrement, mode clearing, update, and recycle decision.
- `ufs_reclaim` writes final updates, releases device vnode, frees quota state, and frees dirhash state.
- `ufs_balloc_range` allocates blocks over a byte range while locking pages so stale disk contents cannot become visible to racing readers.
- `ufs_truncate_retry` wraps truncate in WAPBL transactions and retries `EAGAIN` until size reaches target.
- `ufs_truncate_all` truncates file data plus UFS2 extended attribute area.

Important behavior:
- Uses WAPBL begin/end around metadata-changing operations.
- Panics if an unlinked inode reaches inactive with mode zero but nonzero size or blocks after cleanup.
- Page-cache handling marks pages dirty and clears `PG_RDONLY` only when allocation succeeds and pages are fully backed.
