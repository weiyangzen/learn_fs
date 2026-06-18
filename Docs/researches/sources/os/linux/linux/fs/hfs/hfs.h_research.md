# File Research: sources/os/linux/linux/fs/hfs/hfs.h

Purpose: Small HFS-private header that includes shared on-disk/common definitions and defines `struct hfs_readdir_data`.

Key structure:
- `struct hfs_readdir_data` stores list linkage, owning `struct file *`, and last catalog key for an active directory enumeration.

Dependencies and integration:
- Used by `dir.c` and `catalog.c` to adjust open directory iterators when catalog entries are deleted before their current position.

Risk notes:
- The structure is protected by `HFS_I(dir)->open_dir_lock`; callers must preserve that locking discipline.
