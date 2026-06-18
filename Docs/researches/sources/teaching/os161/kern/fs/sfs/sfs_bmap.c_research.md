# File Research: sources/teaching/os161/kern/fs/sfs/sfs_bmap.c

Maps SFS logical file blocks to disk blocks and truncates files.

`sfs_bmap`:
- Handles `SFS_NDIRECT` direct block pointers first.
- Allocates missing data blocks when `doalloc` is true, updates inode pointers, and marks the vnode dirty.
- Handles one indirect block (`SFS_NINDIRECT == 1`), using a static 512-byte buffer protected by the VFS biglock.
- Allocates the indirect block on demand, clears the indirect buffer for new indirect blocks, reads existing indirect blocks, updates entries, and writes dirty indirect blocks.
- Returns `EFBIG` for file blocks beyond supported direct plus single-indirect capacity.
- Panics if a nonzero block pointer refers to a block marked free in the freemap.

`sfs_itrunc`:
- Rounds target length up to block count.
- Frees direct blocks past the new length.
- Reads the indirect block when present, frees indirect data blocks past the new EOF, writes the indirect block if partially changed, or frees the indirect block if now empty.
- Updates `sfi_size` and marks inode dirty.

Notable constraints:
- Uses static indirect buffers, so correctness depends on `vfs_biglock`.
- The truncation comparison uses block-index logic tightly tied to the simple one-indirect layout.
