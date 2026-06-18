# File Research: sources/os/linux/linux-stable/fs/kernfs/kernfs-internal.h

Internal kernfs header tying together inode, directory, file, symlink, mount, and global-lock implementation details.

Defines:
- `struct kernfs_iattrs`: persistent uid/gid/timestamps and simple xattr state.
- `struct kernfs_root`: root node, ID allocator, syscall ops, superblock list, deactivation wait queue, rwsems, rename lock, and RCU lifetime.
- `KN_DEACTIVATED_BIAS`: active-reference deactivation bias.
- `struct kernfs_super_info`: per-superblock root and namespace tag.

Important helpers:
- `kernfs_root()` resolves a node’s root using RCU parent access.
- `kernfs_rcu_name()` and `kernfs_parent()` provide lockdep-aware access to rename-sensitive fields.
- `kernfs_dentry_node()` maps a positive dentry to its kernfs node.
- Directory revision helpers store/recheck `dentry->d_time`.

Exports internal cross-file interfaces:
- Inode operations and xattr handlers from `inode.c`.
- Directory operations and active-reference helpers from `dir.c`.
- File operations and open-file draining helpers from `file.c`.
- Symlink inode ops from `symlink.c`.
- `kernfs_locks` global lock table from `mount.c`.
