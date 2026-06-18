# File Research: sources/os/linux/linux/fs/kernfs/kernfs-internal.h

Purpose: Internal kernfs header defining private root, superblock, inode-attribute, dentry helper, and lock helper contracts shared by kernfs implementation files.

Key definitions:
- `struct kernfs_iattrs` stores persistent uid/gid/timestamps and simple xattrs.
- `struct kernfs_root` owns node ID allocation, syscall ops, superblock list, rwsems, rename lock, deactivate waitqueue, and xattr cache.
- `struct kernfs_super_info` maps a superblock to a kernfs root and namespace tag.
- Inline helpers derive root, parent, names, dentry nodes, directory revision checks, and per-node hashed mutexes.
- Declares cross-file operations for inode, dir, file, symlink, and mount support.

Dependencies and integration:
- Includes public `linux/kernfs.h` and VFS/fs_context/xattr headers.
- `kernfs_root()` uses RCU parent dereference and assumes parent nodes are directories.
- Hashed locks come from global `kernfs_locks`, initialized in `mount.c`.

Concurrency and risk notes:
- Parent/name access helpers encode lockdep expectations for `kernfs_rwsem`, rename lock, RCU, and dead-node cases.
- `kernfs_node_lock_ptr()` hashes node addresses, so unrelated nodes may serialize on the same mutex.
- This header is central to lock ordering and lifetime assumptions across kernfs.
