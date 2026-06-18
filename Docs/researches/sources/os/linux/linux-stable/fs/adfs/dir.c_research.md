# File Research: sources/os/linux/linux-stable/fs/adfs/dir.c
- Purpose: Implements common ADFS directory reading, updating, lookup, iteration, and dentry comparison.
- Main functions: `adfs_dir_read_buffers`, `adfs_dir_read_inode`, `adfs_dir_update`, `adfs_object_fixup`, `adfs_iterate`, `adfs_dir_lookup_byname`, `adfs_lookup`.
- Directory abstraction: Uses `adfs_dir_ops` so old F-format and F+ directory implementations share VFS-level logic.
- Name handling: Converts special ADFS names, optionally appends filetype suffixes, and performs case-insensitive dentry hashing/comparison.
- Concurrency: Uses a directory read/write semaphore around iteration and update operations.
- Operation tables: Exports `adfs_dir_operations`, `adfs_dentry_operations`, and `adfs_dir_inode_operations`.
- Risks: Directory buffer read/update paths depend on correct indirect address mapping and validation by the selected directory format implementation.
