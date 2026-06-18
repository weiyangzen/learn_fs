# File Research: sources/os/linux/linux/fs/omfs/omfs.h

Internal OMFS header for in-memory state, helpers, and cross-file declarations.

Key contents:
- Includes the on-disk format header `omfs_fs.h`.
- Defines `struct omfs_sb_info`, the filesystem-private superblock state.
- Stores block counts, bitmap inode, root inode, filesystem and system block sizes, mirror count, cluster size, block shift, in-memory bitmap, bitmap lock, uid/gid, and masks.
- Provides `clus_to_blk()`, converting OMFS cluster/block numbers to Linux sector/block numbers using `s_block_shift`.
- Provides `OMFS_SB()` for typed access to `sb->s_fs_info`.

Declared module interfaces:
- Bitmap allocation/free/count functions from `bitmap.c`.
- Directory operation tables and helpers from `dir.c`.
- File operation/address-space tables and extent helpers from `file.c`.
- Inode/super helpers from `inode.c`.

Notable detail:
- The header declares `omfs_reserve_block()` and `omfs_find_empty_block()`, but the listed implementation files do not define them; they appear to be stale declarations.
