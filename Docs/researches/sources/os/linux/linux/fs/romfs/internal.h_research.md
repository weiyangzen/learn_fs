# File Research: sources/os/linux/linux/fs/romfs/internal.h

## Purpose
Private ROMFS header defining inode-private state, convenience helpers, and internal storage/mmap declarations.

## Key Types
- `struct romfs_inode_info`
  - Embeds `struct inode vfs_inode`.
  - `i_metasize`: size of non-data inode metadata.
  - `i_dataoffset`: byte offset of file data from filesystem start.

## Helpers
- `romfs_maxsize(sb)`: returns maximum image size from `sb->s_fs_info`.
- `ROMFS_I(inode)`: converts a VFS inode to `struct romfs_inode_info`.

## Declarations
- `romfs_ro_fops`
  - Uses NOMMU MTD-specific implementation when `!CONFIG_MMU && CONFIG_ROMFS_ON_MTD`.
  - Otherwise aliases to `generic_ro_fops`.
- Storage helpers from `storage.c`:
  - `romfs_dev_read()`
  - `romfs_dev_strnlen()`
  - `romfs_dev_strcmp()`

## Research Notes
This header is the narrow internal API between ROMFS superblock/inode code, storage access, and optional NOMMU MTD mmap support.
