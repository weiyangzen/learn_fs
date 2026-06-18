# File Research: sources/os/bsd/netbsd-src/sys/fs/sysvbfs/sysvbfs.h

Read completely: 99 lines.

This is the internal sysvbfs interface header. It defines `struct sysvbfs_node`, which embeds a `genfs_node` and tracks the vnode, BFS inode pointer, mount pointer, advisory lock state, current data block, size, timestamp-update flags, and removal state. It also defines `struct sysvbfs_mount`, containing the NetBSD mount, mounted block-device vnode, and parsed BFS state.

The header declares all sysvbfs vnode operations, VFS operation prototypes through `VFS_PROTOS(sysvbfs)`, the vnode operation vector pointer, genfs operations, `sysvbfs_gop_alloc`, and `sysvbfs_update`.

Important interactions: this header is shared by `sysvbfs.c`, `sysvbfs_vfsops.c`, and `sysvbfs_vnops.c`; it also includes `sysvbfs_args.h` and genfs/specfs headers.

Security/reliability notes: structure fields are mutable vnode state and are protected by normal vnode locking conventions, not by private locks in this header.
