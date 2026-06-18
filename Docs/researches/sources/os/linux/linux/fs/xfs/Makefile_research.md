# File Research: sources/os/linux/linux/fs/xfs/Makefile

Defines the kernel build composition for the XFS module/object.

Key behavior:
- Adds include paths for XFS trace events and `libxfs`.
- Builds `xfs.o` when `CONFIG_XFS_FS` is enabled.
- Compiles `xfs_trace.o` first because trace macros are sensitive to ordering.
- Includes core `libxfs` objects first, including AG, allocation, attribute, bmap, btree, directory, inode, rmap, refcount, superblock, transaction reservation, and type logic.
- Adds realtime shared `libxfs` objects when `CONFIG_XFS_RT` is enabled.
- Adds high-level filesystem objects for I/O, buffers, attributes, directories, discard, errors, export, extent busy tracking, file operations, fsmap, mount, reflink, stats, superblock, sysfs, transactions, verification, and xattrs.
- Adds low-level log and transaction item objects.
- Adds optional quota, ACL, sysctl, compat ioctl, pNFS, DAX memory-failure, live hook, drain, memory-buffer, and in-memory btree objects based on config.
- Adds online scrub object groups under `CONFIG_XFS_ONLINE_SCRUB`.
- Adds online repair object groups under `CONFIG_XFS_ONLINE_REPAIR`.
- Adds realtime scrub/repair and quota scrub/repair files when corresponding features are enabled.

Important interactions:
- `libxfs/xfs_ag.o`, `xfs_ag_resv.o`, `xfs_alloc.o`, and `xfs_alloc_btree.o` from this group are core `libxfs` build inputs.
- Scrub and repair expand the build substantially and depend on Kconfig feature gates.
