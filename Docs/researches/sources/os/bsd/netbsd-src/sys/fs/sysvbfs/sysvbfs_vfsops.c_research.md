# File Research: sources/os/bsd/netbsd-src/sys/fs/sysvbfs/sysvbfs_vfsops.c

Read completely: 451 lines.

This implements sysvbfs mount lifecycle and VFS entry points. `sysvbfs_mount` validates mount arguments, resolves the block device, checks block-device type and permissions, handles update mounts, calls `sysvbfs_mountfs`, and fills statvfs metadata. `sysvbfs_mountfs` invalidates device buffers, opens the block device, allocates `struct sysvbfs_mount`, initializes the BFS layer, and sets mount identity and block-size fields.

Other operations include root vnode lookup by `BFS_ROOT_INODE`, statvfs synthesis from BFS metadata, sync over all mounted vnodes, vnode loading via BFS inode lookup, `vcache_get`-based `vget`, unsupported file-handle conversion, pool/malloc initialization and teardown, and a no-op `sysvbfs_gop_alloc`.

Important interactions: depends on `bfs.h` functions such as `sysvbfs_bfs_init`, `bfs_inode_lookup`, `bfs_inode_alloc`, and `sysvbfs_bfs_fini`. Vnode objects are allocated from `sysvbfs_node_pool` and initialized with `genfs_node_init`.

Security/reliability notes: mount validates device type and mount authorization. NFS file handles are unsupported. Unmount closes the device with `FREAD` even if it may have been opened read/write, which is worth preserving or reviewing carefully if changing mount flags.
