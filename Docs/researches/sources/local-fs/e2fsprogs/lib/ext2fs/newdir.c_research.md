# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/newdir.c

Builds new directory data templates. `ext2fs_new_dir_block()` allocates and initializes a full directory block containing `.` and `..` entries when a directory inode is supplied.

It reserves metadata checksum tail space when enabled and initializes the dirent tail. Filetype fields are set only when the filesystem has the filetype feature.

`ext2fs_new_dir_inline_data()` initializes inline directory data by storing the parent inode in the inline dotdot area and creating the remaining empty dirent record, with big-endian output swabbing when required.
