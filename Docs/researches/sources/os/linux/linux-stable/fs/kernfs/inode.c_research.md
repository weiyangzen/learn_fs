# File Research: sources/os/linux/linux-stable/fs/kernfs/inode.c

Implements kernfs inode attributes, inode instantiation, permission/getattr/setattr, and xattr support.

Key responsibilities:
- `kernfs_iattrs` are allocated lazily with defaults for uid/gid/timestamps and `simple_xattr_limits`.
- `kernfs_setattr()` and `kernfs_iop_setattr()` update persistent kernfs attributes under `root->kernfs_iattr_rwsem`.
- `kernfs_refresh_inode()` copies kernfs mode and persistent attributes into VFS inode state and maintains directory link counts.
- `kernfs_init_inode()` initializes inode operations based on node type:
  - directories use `kernfs_dir_iops` / `kernfs_dir_fops`
  - files use `kernfs_file_fops`
  - links use `kernfs_symlink_iops`
  - empty dirs use `make_empty_dir_inode()`
- `kernfs_get_inode()` obtains or initializes an inode keyed by `kernfs_ino(kn)`.
- `kernfs_evict_inode()` truncates pages, clears inode state, and drops the kernfs node reference.
- `kernfs_iop_permission()` refreshes attributes before delegating to `generic_permission()`.

Xattr behavior:
- Trusted and security xattrs use generic kernfs get/set wrappers.
- User xattrs require `KERNFS_ROOT_SUPPORT_USER_XATTR` and use limited simple xattr storage.
- `kernfs_iop_listxattr()` lists lazily allocated xattrs.

Important locking:
- Attribute reads and writes are serialized with `kernfs_iattr_rwsem`.
- Lazy `kn->iattr` installation uses `try_cmpxchg` to handle concurrent first allocation.
