# File Research: sources/os/linux/linux/fs/efs/super.c

Implements EFS module registration, superblock setup, SGI volume-header parsing, and statfs.

Key behavior:
- Registers a block-device filesystem named `efs`.
- Allocates EFS private inodes from `efs_inode_cache`.
- Provides export operations for inode-number file handles.
- Parses the SGI volume header, validates checksum, scans partition entries, and locates an EFS slice.
- Validates the EFS superblock magic and loads filesystem geometry/free-count fields.
- `fill_super` sets 512-byte block size, reads volume header and superblock, forces read-only mode, installs super/export operations, loads root inode, and creates root dentry.
- Reconfigure always syncs and forces read-only.
- `statfs` reports total/free data blocks, inode counts, fsid, block size, and max name length.

Important interactions:
- Uses SGI partition constants from `<linux/efs_vh.h>` and superblock layout from `<linux/efs_fs_sb.h>`.
- EFS is mounted with `FS_REQUIRES_DEV`.
- All mutation attempts are prevented by read-only mount state and read-only file/block operations.
