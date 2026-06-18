# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_bmap.c

This file maps UFS logical file offsets to physical disk blocks and allocates blocks during writes. It handles direct blocks, single/double/triple indirect blocks, fragments, holes, preallocated negative block markers, synchronous metadata safety, and partial-allocation rollback.

`bmap_read` maps an offset to a disk block and transfer length without allocation. It handles direct blocks through the `DOEXTENT` macro, walks indirect blocks for larger logical block numbers, returns `UFS_HOLE` for missing pointers, limits extents by EOF and `vfs_iotransz`, and returns disk block numbers rather than filesystem block numbers.

`bmap_write` ensures that a block range exists for a write or preallocation request. For direct blocks it grows the previous last fragment to a full block when crossing a block boundary, allocates or reallocates the target fragment/block, zeroes or reads pages as needed, updates `i_db`, `i_blocks`, inode transaction state, and frees old fragments when a reallocation moved them. Directories, quota files, shadow inodes, and synchronous inodes force normal allocation and more conservative zero/write ordering.

For indirect blocks, `bmap_write` determines the required indirection depth, allocates missing indirect blocks synchronously zeroed before linking them, then allocates missing data blocks. It keeps an `ufs_allocated_block` undo table recording newly allocated blocks, their owner pointer location, and free flags. If any later read, write, or allocation fails, `ufs_undo_allocation` removes any installed pointers before freeing blocks to avoid creating double-owned blocks. For `BI_FALLOCATE`, lowest-level data block pointers are stored as negative block numbers.

The very-large-file guard protects the signed 32-bit `i_blocks` field. When `ip->i_blocks` approaches the `VERYLARGEFILESIZE` threshold, allocation checks whether adding metadata or data sectors would exceed `INT_MAX` and returns `EFBIG` before corrupting the count.

`bmap_has_holes` uses file length and allocated block count, including expected indirect metadata blocks, to conservatively detect sparse files. If another thread is in the writer critical region, it reports holes because `i_size` and `i_blocks` cannot be trusted.

`findextent` scans contiguous direct or indirect block-pointer arrays and returns an extent length capped by `fs_maxcontig` or the device transfer size. This is the helper behind read-side clustering in `DOEXTENT`.

`ufs_undo_allocation` is the rollback engine for indirect allocation failure. It first clears inode or indirect-block pointers and logs those pointer updates; only if pointer updates succeed does it free the newly allocated blocks. It adjusts `i_blocks`, marks the inode changed, and writes the inode synchronously on non-logging filesystems so the filesystem does not transiently point at blocks it has returned to free space.

`bmap_find` searches from an offset for the next hole or data block. It checks direct blocks first, then walks indirect levels using cached buffers per level, skips whole missing indirect subtrees when looking for data, and returns `ENXIO` at or beyond EOF. This is suitable for SEEK_HOLE/SEEK_DATA-style behavior.

`bmap_set_bn` overwrites the block pointer for a logical offset, directly in `i_db` or inside the appropriate indirect block. It requires the caller to hold inode locking and to perform transaction logging. It is used by allocation rollback paths such as `ufs_allocsp` undo.

Integration notes: `bmap_write` is called with `i_contents` held for write and assumes truncation is excluded by higher-level locking. Metadata blocks are synchronously zeroed before being linked so crashes do not leave indirect blocks pointing through garbage. Fallocate's negative block numbers must be preserved until later write/read paths convert or zero them appropriately.
