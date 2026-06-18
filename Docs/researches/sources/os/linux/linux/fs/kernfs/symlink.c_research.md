# File Research: sources/os/linux/linux/fs/kernfs/symlink.c

Purpose: Implements kernfs symlink creation and VFS symlink resolution.

Key functionality:
- `kernfs_create_link()` creates a `KERNFS_LINK` node, copies target ownership if persistent attrs exist, optionally copies namespace tag, stores `target_kn`, and holds a reference on the target.
- `kernfs_get_target_path()` builds a relative path from symlink parent to target, walking up to a common base and then reverse-filling target components.
- `kernfs_iop_get_link()` allocates a page-sized path buffer, resolves the link under `kernfs_rwsem`, and returns it via delayed cleanup.
- `kernfs_symlink_iops` wires get_link plus shared kernfs xattr, setattr, getattr, and permission operations.

Dependencies and integration:
- Uses `kernfs_new_node()`, `kernfs_add_one()`, `kernfs_parent()`, and `kernfs_rcu_name()`.
- Shares inode operation helpers from `inode.c`.

Risk notes:
- Path construction is bounded by `PATH_MAX` and returns `-ENAMETOOLONG` on overflow.
- Relative-path generation assumes stable parent/name relationships while `root->kernfs_rwsem` is held.
- A target reference is owned by the symlink node and released through normal kernfs node cleanup paths.
