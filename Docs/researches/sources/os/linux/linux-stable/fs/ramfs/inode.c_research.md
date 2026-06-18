# File Research: sources/os/linux/linux-stable/fs/ramfs/inode.c

## Purpose
Implements ramfs inode creation, directory operations, mount option parsing, superblock setup, filesystem context setup, and registration.

## Main Responsibilities
- `ramfs_get_inode()`: allocates and initializes ramfs inodes using `ram_aops`, unevictable mappings, timestamps, and type-specific inode/file operations.
- `ramfs_mknod()`, `ramfs_create()`, `ramfs_mkdir()`, `ramfs_symlink()`, `ramfs_tmpfile()`: implement object creation with LSM initialization and simple dentry helpers.
- Directory inode ops use simple VFS helpers for lookup, link, unlink, rmdir, rename, and tmpfile.
- `ramfs_show_options()`: reports non-default mount mode.
- `ramfs_parse_param()`: parses `mode=` and intentionally ignores unknown legacy options.
- `ramfs_fill_super()`: sets superblock limits, block size, magic, operations, dentry flags, time granularity, and root inode.
- `ramfs_init_fs_context()` / `ramfs_free_fc()`: allocate/free per-mount ramfs config.
- `ramfs_kill_sb()`: frees fs info and kills anonymous superblock.
- Registers `file_system_type` named `ramfs`.

## Mount State
`struct ramfs_fs_info` stores only mount options, currently root mode. Default mode is `0755`.

## Design
Ramfs is intentionally minimal and page-cache-backed, demonstrating a simple VFS filesystem with no persistent backing store and no custom data tree.
