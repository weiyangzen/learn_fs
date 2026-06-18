# File Research: sources/os/bsd/netbsd-src/sys/fs/sysvbfs/sysvbfs.c

Read completely: 154 lines.

This is the sysvbfs VFS module registration and vnode/VFS operation table file. It declares `MODULE(MODULE_CLASS_VFS, sysvbfs, NULL)`, the `sysvbfs_vnodeop_entries` dispatch table, the `sysvbfs_genfsops` table, and the `sysvbfs_vfsops` table used by `vfs_attach`.

The vnode table wires the flat BFS-backed implementation to NetBSD vnode operations: lookup/create/open/close/access/getattr/setattr/read/write/fsync/remove/rename/readdir/inactive/reclaim/bmap/strategy/print/advlock/pathconf come from sysvbfs-specific code, while unsupported or generic operations are delegated to genfs helpers.

Important interactions: `sysvbfs_vfsops.c` implements mount lifecycle and vnode loading; `sysvbfs_vnops.c` implements the vnode operations registered here; `sysvbfs.h` exports the prototypes and `sysvbfs_genfsops`.

Security/reliability notes: no direct parsing logic here. Risk is dispatch correctness: unsupported filesystem features such as links, directories beyond root, symlinks, fallocate, and fdiscard are explicitly rejected via genfs error helpers.
