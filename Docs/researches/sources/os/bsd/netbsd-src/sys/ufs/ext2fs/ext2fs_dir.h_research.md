# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_dir.h

This header defines ext2 directory entry formats and directory helper macros.

Key definitions:
- `doff_t` as 32-bit directory offset and `EXT2FS_MAXDIRSIZE`.
- `EXT2FS_MAXNAMLEN` as 255.
- `struct ext2fs_direct`: on-disk variable-length directory entry header plus maximum name storage.
- `enum ext2fs_slotstatus` and `struct ext2fs_searchslot`: state used by lookup/insert code to track reusable directory space.
- Ext2 directory file type constants and conversion helpers:
  - `inot2ext2dt`: inode mode to ext2 directory type.
  - `ext2dt2dt`: ext2 directory type to NetBSD `DT_*`.
- `EXT2FS_DIRSIZ` and `EXT2_DIR_REC_LEN`: record length calculations.
- `struct ext2fs_dirtemplate`: template for `.` and `..` directory initialization.

Dependencies:
- `sys/dirent.h`
- `ext2fs_dinode.h`

Design notes:
- The header documents the ext2 rev0/rev1 split of `namlen` and `type`.
- Directory free space is represented by oversized `reclen` fields or zero inode entries.
