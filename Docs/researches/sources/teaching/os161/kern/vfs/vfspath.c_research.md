# File Research: sources/teaching/os161/kern/vfs/vfspath.c

Implements high-level pathname operations. `vfs_open` validates access mode, handles `O_CREAT` with `vfs_lookparent` plus `VOP_CREAT`, otherwise uses `vfs_lookup`, calls `VOP_EACHOPEN`, and handles `O_TRUNC` only for writable opens. On success it returns a referenced vnode.

`vfs_close` decrefs without reporting errors, with comments explaining why close failures are not propagated. Remove, mkdir, rmdir, symlink, and rename-style operations resolve parent directories and final names, call the corresponding VOP, then decref parents. `vfs_link` and `vfs_rename` reject cross-filesystem operations with `EXDEV`.

Symlink support is explicitly partial: `vfs_symlink` and `vfs_readlink` exist, but broader VFS symlink traversal is noted as incomplete.
