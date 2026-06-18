# File Research: sources/os/bsd/dragonflybsd/sys/kern/vfs_init.c

## Summary
Initializes the VFS subsystem and manages filesystem/vnode operation-vector registration.

## Main Responsibilities
- Initializes VFS globals, namei object cache, vnode subsystem, mount subsystem, vnode locking, and namecache.
- Adds/removes vnode operation vectors with default-op filling.
- Maintains registered filesystem types in `vfsconf_list`.
- Registers/unregisters filesystems and handles VFS module load/unload events.

## Important Behavior
`vfs_add_vnodeops()` can either install a static template or allocate a mount-specific copy, then fills NULL VOP slots from `vop_default`. When journal or coherency operations are present, mount vnode dispatch is redirected through those layered ops.

`vfs_register()` rejects duplicate filesystem names, assigns a type number, re-numbers matching `vfs.<fstype>` sysctl nodes, asserts core mount/root/unmount ops, fills missing optional VFS methods with standard defaults, conditionally adds VFS quota accounting methods, then calls filesystem init.

## Risks
Registration mutates the filesystem’s provided `vfsops` vector in place. Unregister refuses active filesystem types via `vfc_refcount`, but otherwise assumes the registered `vfsconf` and ops remain valid.
