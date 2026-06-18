# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufs_bmap.c

## Purpose

Implements UFS logical-to-physical block mapping. It translates file logical offsets or logical block numbers into device offsets, computes contiguous run lengths, and constructs indirect-block traversal paths.

## Main Functions

- `ufs_bmap(struct vop_bmap_args *ap)`: vnode operation wrapper. Validates the logical offset alignment, calls `ufs_bmaparray()`, returns `NOOFFSET` for holes, and converts disk blocks to byte offsets.
- `ufs_bmaparray(struct vnode *vp, ufs_daddr_t bn, ufs_daddr_t *bnp, struct indir *ap, int *nump, int *runp, int *runb)`: core block mapper. Handles direct blocks, indirect blocks, holes, cached indirect blocks, synchronous reads of indirect blocks, and forward/backward sequential run detection.
- `ufs_getlbns(struct vnode *vp, ufs_daddr_t bn, struct indir *ap, int *nump)`: computes the path through single, double, or triple indirect blocks for a target logical block. Negative logical block numbers represent metadata blocks.

## Important Behavior

Direct blocks are read from `ip->i_db[]`; indirect roots come from `ip->i_ib[]`. Physical UFS block pointers are converted with `blkptrtodb()`. If a block pointer is zero, the mapper returns `-1` internally and `NOOFFSET` to callers.

Indirect blocks are addressed as negative logical block numbers on the file vnode. The code uses `findblk()` to avoid disk I/O for unallocated indirect blocks unless a cached buffer exists. When an indirect buffer is not cached, it is read synchronously via `vn_strategy()` using the cached physical offset in `bio2`.

## Dependencies And Integration Points

Relies on `struct inode`, `struct fs`, `struct ufsmount`, buffer cache operations, `ffs_blkatoff` conventions, and macros from `ufsmount.h`: `MNINDIR`, `blkptrtodb`, and `is_sequential`.

## Notes For Future Work

- `ufs_getlbns()` uses `int64_t` for `qblockcnt` to avoid overflow for triple-indirect calculations on 32-bit `long`.
- `runp` and `runb` are returned in blocks from `ufs_bmaparray()` and converted to bytes by `ufs_bmap()`.
- The code assumes callers pass block-aligned logical offsets to `ufs_bmap()`.
