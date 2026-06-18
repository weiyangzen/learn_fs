# File Research: sources/os/linux/linux/fs/kernfs/mount.c

Purpose: Implements kernfs superblock creation, mount retrieval, export file handles, path display hooks, kill_sb cleanup, and global kernfs cache/lock initialization.

Key functionality:
- Defines `kernfs_sops` with statfs, inode eviction, show_options/show_path, and explicit no freeze/thaw behavior.
- Provides export operations for encoding kernfs node IDs and resolving file handles back to dentries.
- `kernfs_node_dentry()` reconstructs a dentry path for invariant-parent roots by walking ancestor names.
- `kernfs_fill_super()` configures superblock flags, xattrs, export ops, root inode/dentry, and dentry ops.
- `kernfs_get_tree()` shares or creates anonymous superblocks based on root and namespace tag.
- `kernfs_kill_sb()` removes the superblock from the root’s mounted-super list and frees `kernfs_super_info`.
- `kernfs_init()` creates slab caches and initializes global hashed node mutexes.

Dependencies and integration:
- Uses `kernfs_get_inode()` from `inode.c`, `kernfs_dops` from dir code, and `kernfs_xattr_handlers`.
- Superblock list is consumed by `kernfs_notify_workfn()` in `file.c`.
- Export support depends on `kernfs_find_and_get_node_by_id()` and parent lookup helpers outside this file.

Concurrency and risk notes:
- Superblock list updates are protected by `kernfs_supers_rwsem`; root tree walks use `kernfs_rwsem`.
- `kernfs_set_super()` clears `kfc->ns_tag`, transferring ownership expectations to the new superblock setup.
- `kernfs_node_dentry()` requires `KERNFS_ROOT_INVARIANT_PARENT`; otherwise it returns `-EINVAL`.
