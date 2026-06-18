# File Research: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_extern.h

Central external declaration header for ext2fs. It forward-declares kernel/VFS types, exports inode/dinode pools, and declares functions from allocation, block allocation, bmap, inode, lookup, subr, vfsops, readwrite, and vnops modules.

Important integration points include VFS mount/unmount/statfs/sync/vget/fh conversion/superblock update, VOP implementations for create/remove/link/rename/mkdir/rmdir/symlink/readlink/access/getattr/setattr/fsync/reclaim, and `IS_EXT2_VNODE(vp)` based on `VT_EXT2FS`. It also exports ext2fs vnode operation tables for regular, special, and FIFO vnodes.
