# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_inode.c

This file implements inode metadata update, indirect-block truncation, top-level truncation, inactive cleanup, and reclaim for DragonFlyBSD ext2.

Key responsibilities:
- Flush dirty inode timestamps/metadata to disk.
- Grow or shrink classic direct/indirect block files.
- Recursively free single/double/triple indirect block trees.
- Zero partial blocks when shrinking.
- Release blocks and free inodes when link count reaches zero.
- Remove reclaimed inodes from the inode hash and free memory.

Important functions:
- `ext2_update`: Applies pending times via `ext2_itimes`, reads the inode table block, converts inode to on-disk form with `ext2_i2ei`, and writes or delays the buffer.
- `ext2_indirtrunc`: Recursively zeros and frees indirect block pointers in LIFO order.
- `ext2_ind_truncate`: Handles file extension through `ext2_balloc`, shrink-to-length, inode pointer updates-before-free, buffer truncation, direct/indirect freeing, and `i_blocks` accounting.
- `ext2_ext_truncate`: Extent truncate placeholder; returns `EINVAL`.
- `ext2_truncate`: Dispatches short symlinks, no-op size updates, extent truncate, or indirect truncate.
- `ext2_inactive`: On last inactive reference, truncates and frees unlinked writable inodes; writes pending times.
- `ext2_reclaim`: Flushes lazy modifications, removes inode from ihash, releases device vnode, and frees the inode.

Important interactions:
- Calls `ext2_balloc`, `ext2_blkfree`, `ext2_vfree`, `ext2_i2ei`, `ext2_itimes`, and `ext2_ihashrem`.
- Uses VM vnode pager sizing and buffer truncation to keep cache state coherent.

Notable behavior and risks:
- Extent-backed truncation is unsupported and returns `EINVAL`.
- Truncation writes the shortened inode before freeing blocks to prefer leak-over-corruption crash behavior.
- Triple indirect truncation is marked as untested in a comment.
