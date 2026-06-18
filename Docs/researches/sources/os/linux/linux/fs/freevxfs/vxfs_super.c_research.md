# File Research: sources/os/linux/linux/fs/freevxfs/vxfs_super.c

Read status: complete, 347 lines.

Purpose: mounts, registers, and tears down the FreeVxFS filesystem.

Key flow:
- Defines module metadata and `vxfs_inode_cachep`.
- `vxfs_put_super()` releases fileset/header/list inodes, raw superblock buffer, and superblock-private allocation.
- `vxfs_statfs()` fills basic statfs fields from the raw VxFS superblock.
- `vxfs_reconfigure()` always syncs and forces read-only.
- Super operations allocate/free private VxFS inodes, evict inodes, put superblock, and statfs.
- `vxfs_try_sb_magic()` reads candidate superblock locations and compares raw magic with expected endian encoding.
- `vxfs_fill_super()` forces read-only, allocates `vxfs_sb_info`, finds little-endian UnixWare or big-endian HP-UX superblock, checks VxFS version 2-4, sets block size, reads OLT, reads fileset headers, loads root inode, and creates root dentry.
- Registers `file_system_type` named `vxfs`, requiring a block device, with fs_context get-tree/reconfigure hooks.
- Module init creates a usercopy-aware inode cache and registers the filesystem; exit unregisters, waits for RCU, and destroys the cache.

Important dependencies: block-device mount helper `get_tree_bdev`, VFS fs_context, `register_filesystem`, OLT/fileset/inode readers.

Risk notes:
- The driver is strictly read-only.
- Superblock discovery is limited to known UnixWare and HP-UX offsets/endianness.
- Some mount failure paths free `s_fs_info` resources locally; normal unmount uses `put_super`.
