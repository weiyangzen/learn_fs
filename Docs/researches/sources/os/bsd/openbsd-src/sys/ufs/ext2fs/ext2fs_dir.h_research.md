# File Research: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_dir.h

Defines ext2 directory entry layout and helper types. `struct ext2fs_direct` stores inode, record length, name length, file type, and max 255-byte name. `struct ext2fs_searchslot` records directory insertion/free-space search state.

The file defines ext2 directory file type ids, `inot2ext2dt()` conversion from inode mode type to ext2 directory type, `EXT2FS_DIRSIZ()` record size rounding, max directory size, and `struct ext2fs_dirtemplate` for `.` and `..` initialization.
