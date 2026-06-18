# File Research: sources/os/bsd/netbsd-src/sys/fs/puffs/puffs_vfsops.c

This file implements PUFFS VFS operations and module registration. It defines the `puffs` VFS module depending on `putter`, the putter callback table, genfs hooks, the VFS operation table, and the vnode operation-vector list.

`puffs_vfsop_mount()` validates user-supplied `puffs_kargs`: data length, protocol version, kernel and file-handle flags, spare fields, file-handle sizes including NFS v2/v3 limits, printable type/from names, message size bounds, root vnode type/size, and statvfs setup. It builds the runtime filesystem name with `PUFFS_TYPEPREFIX`, initializes mount stat data before later VFS stat calls can deadlock, allocates `struct puffs_mount`, attaches the putter instance using the caller pid/fd, initializes locks/CVs/queues, records root metadata and compat mode, starts `puffs_sop_thread()`, and assigns a fsid.

`puffs_vfsop_start()` transitions the mount to running. `puffs_vfsop_unmount()` first flushes vnodes, optionally asks the user server via `PUFFS_VFS_UNMOUNT`, then on success or force marks the filesystem dead, detaches putter, waits for mount references, stops the sop thread with `PUFFS_SOPREQSYS_EXIT`, destroys synchronization primitives, and frees the mount. `puffs_vfsop_root()` maps the root cookie to a locked vnode without a userland trip.

`puffs_vfsop_statvfs()` delegates to userland except during mount setup, then copies statvfs info back into kernel mount fields. `pageflush()` and `puffs_vfsop_sync()` flush regular vnode page cache and issue `PUFFS_VFS_SYNC`. `puffs_vfsop_fhtovp()` and `puffs_vfsop_vptofh()` implement NFS-style file-handle conversion with support for static, dynamic, and passthrough handles. `puffs_vfsop_loadvnode()` allocates and initializes `puffs_node` objects for vcache-created vnodes.

Initialization/done manage `puffs_pnpool`, `puffs_vapool`, and message-interface pools. `puffs_vfsop_extattrctl()` forwards filesystem-level extended-attribute control to userland, carefully retaining/unlocking node state around the wait.
