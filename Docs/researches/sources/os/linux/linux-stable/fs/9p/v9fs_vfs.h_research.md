# File Research: sources/os/linux/linux-stable/fs/9p/v9fs_vfs.h
- Purpose: Declares VFS-facing 9P operations and common VFS helpers.
- Main declarations: Filesystem type, address-space ops, file ops, dir ops, dentry ops, inode cache, inode allocation/init, stat conversion, refresh, setattr, and invalidate helpers.
- Constants: Defines lock timeout, stat-to-inode flags, and `QID2INO` conversion for deriving inode numbers from 9P qids.
- Integration: Shared by superblock, inode, dentry, file, dir, xattr, and ACL implementation files.
- Research notes: This is the VFS contract header for the 9P subtree.
