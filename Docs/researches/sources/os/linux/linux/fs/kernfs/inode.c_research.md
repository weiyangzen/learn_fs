# File Research: sources/os/linux/linux/fs/kernfs/inode.c

Purpose: Provides kernfs inode operations, persistent inode attributes, xattr storage, inode creation/refresh, permission checks, and eviction behavior.

Key functionality:
- Lazily allocates `struct kernfs_iattrs` with default uid/gid/timestamps and simple xattr limits.
- `kernfs_setattr()` and VFS `kernfs_iop_setattr()` update persistent kernfs attributes and mirror them into live inodes.
- `kernfs_refresh_inode()` copies mode/attrs from `kernfs_node` to inode and maintains directory link counts.
- `kernfs_get_inode()` uses `iget_locked()` keyed by kernfs inode number and initializes file, dir, or symlink operations by node type.
- Xattr handlers expose trusted/security/user xattrs, with user xattrs gated by `KERNFS_ROOT_SUPPORT_USER_XATTR`.

Dependencies and integration:
- Exports `kernfs_xattr_handlers` to `mount.c` for superblock setup.
- Uses `ram_aops` from `libfs.c` for kernfs file mappings.
- References `kernfs_dir_iops`, `kernfs_dir_fops`, `kernfs_file_fops`, and `kernfs_symlink_iops`.

Concurrency and risk notes:
- Attribute updates are protected by `root->kernfs_iattr_rwsem`.
- Xattr modification uses the hashed per-node kernfs mutex because multiple superblocks/namespaces can share one node.
- Lazy allocation uses `try_cmpxchg()` to avoid duplicate persistent attribute installation.
- `kernfs_iop_permission()` returns `-ECHILD` for RCU/MAY_NOT_BLOCK permission checks, forcing blocking revalidation.
