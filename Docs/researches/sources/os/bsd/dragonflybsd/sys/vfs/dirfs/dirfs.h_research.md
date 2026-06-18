# File Research: sources/os/bsd/dragonflybsd/sys/vfs/dirfs/dirfs.h

Read completely: 283 lines.

## Role

This header defines DragonFlyBSD dirfs shared structures, flags, macros, globals, inline reference helpers, and function prototypes. Dirfs is a vkernel filesystem that exposes a host directory tree through DragonFly vnode operations.

## Main Contents

- Allocation type declarations:
  - `M_DIRFS`
  - `M_DIRFS_NODE`
  - `M_DIRFS_MISC`
- State and cache flags:
  - `DIRFS_NOFD`
  - `DIRFS_ROOT`
  - `DIRFS_PASVFD`
  - `DIRFS_NODE_RD`
  - `DIRFS_NODE_WR`
  - `DIRFS_NODE_EXE`
- Buffer-cache constants:
  - `BSIZE` is 16384.
  - `BMASK` is `BSIZE - 1`.
- Debugging macros:
  - `dbg()`
  - `debug_node()`
  - `debug_node2()`
- Locking macros:
  - `dirfs_node_lock()`
  - `dirfs_node_unlock()`
  - `dirfs_mount_lock()`
  - `dirfs_mount_unlock()`
  - token helpers for mount-level serialization.
- `struct dirfs_node`:
  - vnode type, state flags, passive-fd cache entry, inode-tree entry, refcount, host fd, parent pointer, vnode pointer, name, advisory lock state, node lock, stat-derived metadata, and file size.
- `struct dirfs_mount`:
  - inode tree, passive fd list, mount lock/token, root node, VFS mount pointer, read-only state, fd counters, vkernel uid/gid, and host root path.
- Conversion macros between VFS mounts/vnodes and dirfs objects.
- Global sysctl-backed variables for debug level and passive fd cache stats.
- Inline node reference helpers:
  - `dirfs_node_ref()`
  - `dirfs_node_unref()`
  - `dirfs_node_setflags()`
  - `dirfs_node_clrflags()`
- Prototypes shared by `dirfs_subr.c`, `dirfs_vfsops.c`, and `dirfs_vnops.c`.

## Important Interactions

- The header exposes host libc-style operations that are temporarily needed in `_KERNEL_VIRTUAL`, including `getdirentries()` and `statfs()`.
- `dirfs_vfsops.c` defines the globals and memory allocation types declared here.
- `dirfs_subr.c` implements node, fd, path, permission, and attribute helpers.
- `dirfs_vnops.c` implements the vnode operation table declared as `dirfs_vnode_vops`.

## Research Notes

- The node structure stores host stat fields directly, making it the cache of host filesystem metadata for VFS operations.
- `dn_refcnt` tracks dirfs node lifetime independently of vnode references; children, passive fd cache, and vnode association all hold node refs.
- The passive fd cache is central to avoiding repeated path walks and enabling openat/fstatat-style operations.
