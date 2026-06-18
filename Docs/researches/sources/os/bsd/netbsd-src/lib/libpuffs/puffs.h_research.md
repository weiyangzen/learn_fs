# File Research: sources/os/bsd/netbsd-src/lib/libpuffs/puffs.h

This public libpuffs header defines the user-facing puffs API, data structures, flags, callback table, and helper prototypes. It includes kernel vnode, mount, namei, stat, statvfs, and puffs message-interface definitions.

Key data structures include `puffs_pathobj`, `puffs_pathinfo`, `puffs_kcache`, `puffs_node`, `puffs_cn`, and the large `puffs_ops` callback table. `puffs_node` stores vnode-like attributes, private data, optional built path, mount pointer, list linkage, and optional cache information. `puffs_cn` wraps kernel component-name data, credentials, and a built full path.

The header defines lib flags such as `PUFFS_FLAG_BUILDPATH`, `PUFFS_FLAG_OPDUMP`, `PUFFS_FLAG_HASHPATH`, and `PUFFS_FLAG_PNCOOKIE`, kernel/lib flag masks, puffs-specific IO/access/fsync constants, setattr/write flags, mount options, and dirent helper macros. `PUFFSOP_PROTOS`, `PUFFSOP_INIT`, `PUFFSOP_SET`, and `PUFFSOP_SETFSNOP` help filesystems declare and install operation callbacks.

The API covers lifecycle (`puffs_init`, `puffs_mount`, `puffs_mainloop`, `puffs_exit`, `puffs_daemon`, `puffs_cancel`), state/configuration, root handling, node allocation/removal/accessors, new-node reply setters, generic fs and genfs helpers, vattr conversion, credentials/access checks, call-context yield/continue/schedule, cache invalidation/flush, path construction, error notification, suspension, and frame-buffer/frame-vector operations.

The header also declares `PUFFSOP_PROTOS(puffs_null)`, making the null filesystem helper visible as a convenience, with an inline comment marking it as questionable public exposure.
