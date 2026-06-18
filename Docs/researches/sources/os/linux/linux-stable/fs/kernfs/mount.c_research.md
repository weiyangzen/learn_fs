# File Research: sources/os/linux/linux-stable/fs/kernfs/mount.c

Implements kernfs superblock operations, export handles, mount/get_tree plumbing, superblock lifetime, and kernfs global initialization.

Core superblock behavior:
- `kernfs_sops` provides statfs, inode eviction, mount option/path display, and explicitly disables freeze/thaw hooks to avoid sysfs suspend/hibernate deadlocks.
- `kernfs_statfs()` uses `simple_statfs()` and UUID-derived fsid.
- `kernfs_fill_super()` initializes kernfs superblock flags, magic, xattr handlers, optional export ops, root inode, root dentry, and dentry ops.

Export support:
- `kernfs_encode_fh()` encodes the 64-bit kernfs node ID.
- `__kernfs_fh_to_dentry()` resolves `FILEID_KERNFS` and compatibility `FILEID_INO32_GEN*` handles back to nodes.
- Parent resolution and dentry construction use `kernfs_find_and_get_node_by_id()`, `kernfs_get_inode()`, and `d_obtain_alias()`.

Mount helpers:
- `kernfs_get_tree()` allocates `kernfs_super_info`, uses `sget_fc()` to share superblocks by root and namespace, fills new superblocks, assigns UUIDs, and links them under `root->supers`.
- `kernfs_kill_sb()` removes the superblock from the root list, kills the anonymous superblock, and frees `kernfs_super_info`.
- `kernfs_free_fs_context()` frees fs context storage.

Dentry path helper:
- `kernfs_node_dentry()` walks from root to target using invariant-parent assumptions and unlocked positive lookups.

Initialization:
- Creates slab caches for `kernfs_node` and `kernfs_iattrs`.
- Allocates and initializes hashed global open-file mutexes.
