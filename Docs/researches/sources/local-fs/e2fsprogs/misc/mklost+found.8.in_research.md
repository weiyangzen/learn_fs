# File Research: sources/local-fs/e2fsprogs/misc/mklost+found.8.in

`mklost+found.8.in` is the manual page template for the `mklost+found` utility.

Documented purpose:
- Create a `lost+found` directory in the current working directory on a mounted ext2/ext3/ext4 filesystem.
- Preallocate directory blocks so `e2fsck` can reconnect many unlinked files without needing to allocate new data blocks during recovery.

Options:
- None.

Research notes:
- The manual describes the user-space mounted-filesystem companion to `mke2fs.c`'s internal `create_lost_and_found()` bootstrap function.
- The operational goal is recovery robustness: make room in the directory before a damaged filesystem needs fsck repair.
