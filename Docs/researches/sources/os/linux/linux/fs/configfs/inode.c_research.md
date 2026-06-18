# File Research: sources/os/linux/linux/fs/configfs/inode.c

## Purpose
Implements configfs inode creation and persistent inode attribute handling.

## Main Elements
- `configfs_setattr()`: persists changed uid/gid/timestamps/mode into `sd->s_iattr`, calls `simple_setattr()`, and handles setgid clearing rules.
- `configfs_new_inode()`: allocates a new inode, assigns a unique inode number, uses `ram_aops`, installs default operations, and applies saved or default attributes.
- Lockdep support: `configfs_set_inode_lock_class()` assigns lock classes for nested default-group inodes.
- `configfs_create()`: validates dentry state, creates a configfs inode, and applies lock class metadata.
- `configfs_get_name()`: returns the VFS dentry name for dirs/links or attribute `ca_name` for text/bin attributes.

## Dependencies And Integration
Used by `dir.c`, `file.c`, `symlink.c`, and `mount.c` whenever configfs materializes VFS objects. Persistent attributes are stored on `struct configfs_dirent`.

## Risk Notes
`sd->s_iattr` allocation happens lazily on first setattr and must remain tied to dirent lifetime. Lockdep class depth for default groups is important to avoid false or real recursive inode-lock issues during group attach/detach.
