# File Research: sources/os/linux/linux-stable/fs/configfs/mount.c

This file implements configfs filesystem registration, root superblock creation, filesystem pinning, and module lifecycle.

Key responsibilities:
- Defines configfs magic, root group, root dirent, and dirent cache.
- Implements `configfs_fill_super()` for `get_tree_single()`.
- Exposes `configfs_pin_fs()` and `configfs_release_fs()` for internal users that need the configfs root.
- Registers configfs as a filesystem and creates the sysfs mount point `kernel_kobj/config`.

Important control flow:
- `configfs_fill_super()` creates the root inode, root dentry, initializes root group state, attaches root dirent, installs default dentry ops, and marks the root dentry `DCACHE_DONTCACHE`.
- `configfs_init()` creates `configfs_dir_cachep`, creates the sysfs mount point, and registers the filesystem.
- `configfs_exit()` unregisters the filesystem, removes the sysfs mount point, and destroys the dirent cache.
- `configfs_free_inode()` frees symlink bodies stored in `inode->i_link`.

Dependencies:
- Uses inode helpers from `inode.c` and directory operations from `dir.c`.
- Exposes pinning used by subsystem registration and dependency APIs.

Risks and invariants:
- `configfs_root` is static and is not freed like regular dirents.
- `simple_pin_fs()` maintains a shared internal mount and reference count.
- Root group identity is used by `configfs_is_root()`.
