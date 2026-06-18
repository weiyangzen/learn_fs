# File Research: sources/os/linux/linux-stable/fs/kernfs/symlink.c

Implements kernfs symlink creation and VFS get_link behavior.

Key behavior:
- `kernfs_create_link()` creates a `KERNFS_LINK` node with mode `0777`, ownership copied from target attributes when present, optional namespace inherited from target, and a held reference to `target`.
- `kernfs_get_target_path()` constructs a relative path from the symlink parent to target by walking up to a common base, adding `../`, then reverse-filling the target path components.
- `kernfs_getlink()` protects parent/name traversal with `root->kernfs_rwsem`.
- `kernfs_iop_get_link()` allocates a PAGE_SIZE buffer, fills it with the relative target path, and registers `kfree_link` cleanup.

Exports:
- `kernfs_symlink_iops` supports listxattr, get_link, setattr, getattr, and permission through shared kernfs inode helpers.
