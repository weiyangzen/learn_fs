# File Research: sources/os/bsd/netbsd-src/sys/fs/union/union.h

Read completely: 183 lines.

Defines the public and kernel-private interface for the legacy NetBSD union filesystem. User-visible mount arguments are `struct union_args`, with mount placement flags `UNMNT_ABOVE`, `UNMNT_BELOW`, and `UNMNT_REPLACE`.

Kernel-only definitions include `struct union_mount`, which records the upper and lower root vnodes, mount credentials, creation mode, and operation mode. `struct union_node` is the per-union-vnode object; it tracks upper/lower vnodes, parent and directory references, saved lookup path, lower-open count, hash-cache flags, directory-cache state, and cached upper/lower file sizes. Comments document lock ownership for fields and the lock order as vnode then `un_lock`.

The header declares union vnode allocation, copy-up, shadow directory, whiteout, rmdir checking, directory cache, vnode close/removal, load/free/init/done hooks, VFS prototypes, vnode operation vector pointer, and conversion macros such as `VTOUNION()`, `UPPERVP()`, `LOWERVP()`, `OTHERVP()`, and `LOCKVP()`.

Risks and notes: this interface exposes detailed internals to the implementation and relies heavily on lock ordering conventions. The same include guard name is also used by `unionfs/unionfs.h`, so both headers are not designed to be included in the same translation unit.
