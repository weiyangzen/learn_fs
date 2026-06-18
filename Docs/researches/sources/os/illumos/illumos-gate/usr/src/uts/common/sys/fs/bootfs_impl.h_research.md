# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/bootfs_impl.h

This private header defines the in-kernel bootfs data structures.

Node model:
- `bootfs_node_t` is the filesystem-specific vnode data for bootfs.
- It stores entry name, vnode, AVL tree of directory entries, AVL/list linkage, physical-memory address, size, parent pointer, and attributes.
- The file comments state bootfs is read-only and node contents are immutable, so node locking is unnecessary.

Filesystem state:
- `bootfs_stat_t` exposes kstat counters for files, directories, bytes, duplicates, and discards.
- `bootfs_t` stores VFS pointer, mount path, root node, kstat pointer, all-node list, minor number, inode count, and stats.

Functions and globals:
- Construction/destruction for `bootfs_t`.
- Node cache constructor/destructor.
- Vnode operations table and template.
- Externs for node cache and bootfs major number.

Dependencies and relationships:
- Uses AVL for directory contents and list linkage for all-node tracking.
- Designed for a persistent-memory boot filesystem presented through vnode/VFS interfaces.
