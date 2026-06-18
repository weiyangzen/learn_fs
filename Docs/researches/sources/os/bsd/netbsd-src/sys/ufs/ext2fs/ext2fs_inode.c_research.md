# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_inode.c

This file implements ext2fs inode size/block-count helpers, inactive handling, inode disk updates, and truncation/freeing of direct and indirect blocks.

Key public functions:
- `ext2fs_size`: returns inode size, combining high size bits for regular files.
- `ext2fs_setsize`: updates inode size and enables `LARGEFILE` feature when needed.
- `ext2fs_nblock`: returns block count, handling ext4 huge-file encoding.
- `ext2fs_setnblock`: stores block count, using huge-file encoding when needed and supported.
- `ext2fs_inactive`: handles last vnode reference, truncating unlinked files and marking deletion time.
- `ext2fs_update`: writes the in-memory inode to its on-disk inode table slot.
- `ext2fs_truncate`: grows or shrinks files and frees blocks beyond EOF.

Key internal function:
- `ext2fs_indirtrunc`: recursively frees blocks referenced by single, double, or triple indirect blocks.

Important behavior:
- Character/block devices, FIFOs, and sockets ignore truncation.
- Short symlinks stored in the inode block array are cleared directly when truncated to zero.
- File growth allocates the last byte through `ufs_balloc_range` and updates UVM vnode size.
- File shrink zeroes the post-EOF region in a partial final block, updates inode size before freeing, writes pointer removals before block frees, truncates buffers, then frees indirect and direct blocks.
- Crash safety follows traditional UFS/ext2 ordering: remove pointers from inode/indirect blocks before returning blocks to the free bitmap.
- `ext2fs_indirtrunc` reads indirect blocks using known disk block numbers because bmap may no longer resolve metadata after pointers are cleared.

Dependencies:
- UFS inode and mount structures.
- Ext2fs allocation/freeing and update helpers.
- NetBSD buffer cache, UVM vnode sizing, and vnode lifecycle APIs.

Notable implementation risks:
- Triple indirect support is explicitly noted as untested.
- Truncation logic depends on careful temporary restoration of old block pointers while freeing blocks.
- Extent-backed inode truncation is not separately handled in this file; this is classic block-pointer truncation logic.
