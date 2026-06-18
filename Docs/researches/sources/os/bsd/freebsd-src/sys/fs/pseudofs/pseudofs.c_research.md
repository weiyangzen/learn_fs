# File Research: sources/os/bsd/freebsd-src/sys/fs/pseudofs/pseudofs.c

## Purpose

Implements the core pseudofs framework: node allocation, tree construction, destruction, mount/unmount/root/statfs operations, filesystem initialization, and module lifecycle.

## Main Entry Points

Node construction:
- `pfs_alloc_node_flags()` allocates a variable-length `struct pfs_node`, initializes its mutex, name, type, and owning `pfs_info`.
- `pfs_add_node()` attaches a node to a parent directory, rejects duplicate names, allocates file numbers, propagates `PFS_PROCDEP`, and appends to the child list.
- `pfs_fixup_dir_flags()` adds synthetic `.` and `..` nodes.
- `pfs_create_dir()`, `pfs_create_file()`, and `pfs_create_link()` create public directory, regular-file, and symlink nodes with callbacks and flags.
- `pfs_find_node()` finds a child by name.

Node destruction:
- `pfs_destroy()` detaches a node, recursively destroys children, purges associated vnodes, invokes optional destroy callbacks, frees the file number, destroys the mutex, and frees storage.

VFS operations:
- `pfs_mount()` initializes mount flags, fsid, statfs defaults, and `mnt_data`.
- `pfs_cmount()` delegates compatibility mounts to `kernel_mount()`.
- `pfs_unmount()` flushes vnodes with optional force.
- `pfs_root()` obtains the root vnode through the pseudofs vnode cache.
- `pfs_statfs()` is a no-op because `mp->mnt_stat` is already populated.

Lifecycle:
- `pfs_init()` initializes fileno allocation, creates root, adds `.`/`..`, and calls the consumer filesystem’s init callback.
- `pfs_uninit()` destroys the root tree, uninitializes fileno allocation, then calls the consumer uninit callback.
- `pfs_modevent()` loads/unloads the shared vnode cache for the pseudofs module.

## Integration Points

Consumers use the public construction APIs and `PSEUDOFS()` macro from `pseudofs.h`. `procfs` is one such consumer. Vnode realization is delegated to `pseudofs_vncache.c` and operation dispatch to `pseudofs_vnops.c`.

## Risks and Review Notes

The node tree is mostly immutable after filesystem initialization; child list manipulation uses node mutexes but some invariant checks are explicitly not fully locked. Dynamic consumers must be careful with parent-before-child lock ordering documented in `pseudofs.h`.
