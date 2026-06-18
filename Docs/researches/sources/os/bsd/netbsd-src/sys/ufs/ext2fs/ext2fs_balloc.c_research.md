# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_balloc.c

This file implements logical block allocation for file data and indirect block trees.

Key public functions:
- `ext2fs_balloc`: allocates or resolves the physical storage backing a logical block.
- `ext2fs_gop_alloc`: allocates a byte range for the generic pager/write path, extending file size as needed.

Important behavior:
- Direct blocks are handled through the first `EXT2FS_NDADDR` inode block pointers.
- Indirect blocks are resolved with `ufs_getlbns`, using negative logical block numbers for metadata blocks.
- Newly allocated indirect blocks are cleared and written synchronously before being referenced, avoiding pointers to garbage after a crash.
- Data block allocation uses `ext2fs_alloc` and preferred-block hints from `ext2fs_blkpref`.
- On partial failure, allocated blocks are freed, indirect pointers are unwound, invalid buffers are released, and inode block counts are adjusted.

Dependencies:
- UFS inode helpers and `ufs_getlbns`.
- Ext2fs allocation functions from `ext2fs_alloc.c`.
- Buffer cache APIs: `bread`, `getblk`, `bwrite`, `bdwrite`, `brelse`.
- UVM history instrumentation when enabled.

Notable implementation risks:
- The function is built around classic ext2 block pointers; extent-based allocation is not handled here.
- The failure path is complex and depends on `unwindidx`, `allociblk`, and correct pointer restoration.
- One flag update in the deallocation path uses `ip->i_e2fs_flags |= IN_CHANGE | IN_UPDATE`, which mixes inode flags with ext2 disk flags naming; this is worth rechecking when modifying.
