# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_inode.c

This file handles inode updates, truncation, inactive cleanup, and vnode reclamation for FreeBSD ext2fs.

Key responsibilities:
- Flush changed inode state to disk.
- Update timestamps before inode writeback.
- Truncate or extend classic direct/indirect block files.
- Truncate or extend extent-backed files.
- Recursively free indirect blocks and data blocks.
- Remove extent ranges through the extent implementation.
- Free extended attributes and data for unlinked inactive inodes.
- Return inode numbers to the inode bitmap and reclaim vnode-private inode memory.

Important functions:
- `ext2_update`: Converts in-memory inode to disk inode and writes/buffers the inode table block.
- `ext2_indirtrunc`: Recursively clears and frees indirect block subtrees.
- `ext2_ind_truncate`: Handles grow/shrink for classic block-map files.
- `ext2_ext_truncate`: Handles grow/shrink for extent-backed files via `ext4_ext_remove_space`.
- `ext2_truncate`: Dispatches symlink, no-op, extent, or indirect truncation.
- `ext2_inactive`: For zero-link inodes, frees extattrs, truncates data, clears mode, and calls `ext2_vfree`.
- `ext2_reclaim`: Flushes lazy modifications, removes vnode hash entry, and frees inode memory.

Important interactions:
- Uses `ext2_balloc`, `ext2_blkfree`, `ext2_i2ei`, `ext2_extattr_free`, `ext4_ext_remove_space`, and vnode pager/buffer truncation APIs.
- Inactive path coordinates xattr cleanup, block freeing, and inode bitmap freeing.

Notable risks:
- Triple indirect truncation is explicitly noted as untested.
- Extent truncation delegates range removal to `ext2_extents.c`, which has partial-range limitations.
