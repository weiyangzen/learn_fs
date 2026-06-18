# File Research: sources/os/darwin/xnu/bsd/vfs/vfs_support.h

Declares the default and error vnode operation helpers implemented by `vfs_support.c`.

Key behavior:
- Provides include guards and pulls in kernel/VFS headers needed for vnode operation argument types.
- Wraps declarations in `__BEGIN_DECLS`/`__END_DECLS` for C++ compatibility.
- Declares paired `nop_*` and `err_*` functions for vnode operations including namespace mutation, open/close, metadata, I/O, locking, directory enumeration, lifecycle, paging, search, copyfile, block mapping, and monitoring.
- Function declarations mirror the generated `struct vnop_*_args` interfaces consumed by vnode operation vectors.

Dependencies:
- Includes `sys/param.h`, `sys/systm.h`, `sys/kernel.h`, `sys/file.h`, `sys/stat.h`, `sys/proc.h`, `sys/conf.h`, `sys/mount.h`, `sys/vnode.h`, `sys/vnode_if.h`, `sys/malloc.h`, and `sys/dirent.h`.

Research notes:
- This header is the public declaration surface for filesystem fallback VNOP routines.
- It intentionally contains prototypes only; behavior is in `vfs_support.c`.
