# File Research: sources/os/darwin/xnu/bsd/vfs/vfs_support.c

Provides default vnode operation implementations for filesystems that do not supply every VNOP. Most `nop_*` routines report success with minimal side effects, while corresponding `err_*` routines generally return `ENOTSUP` after any necessary cleanup/default behavior.

Key behavior:
- Defines local argument-struct declarations matching generated VNOP interfaces, then implements default/error handlers for create, whiteout, mknod, open, close, access, getattr, setattr, read, write, ioctl, select, exchange, revoke, mmap, fsync, remove, link, rename, mkdir, rmdir, symlink, readdir, readdirattr, readlink, inactive, reclaim, strategy, pathconf, advlock, allocate, bwrite, pagein, pageout, searchfs, copyfile, block translation, blockmap, and monitor.
- Diagnostic `nop_create`, `nop_mknod`, and `nop_symlink` assert that the component name owns a pathname buffer when expected.
- Most `nop_*` operations simply return `0`; most `err_*` operations return `ENOTSUP`, sometimes after invoking the matching `nop_*` to preserve side effects.
- `nop_revoke` delegates to `vn_revoke`; `err_revoke` performs that default revoke path before reporting unsupported.
- `nop_readdirattr` sets actual count and EOF flag to zero; `err_readdirattr` preserves those output initializations before returning unsupported.
- `nop_allocate` reports zero bytes allocated; `err_allocate` preserves that output value before returning unsupported.
- `nop_bwrite` delegates to `buf_bwrite`, while `err_bwrite` returns unsupported.
- `nop_pagein`, `err_pagein`, `nop_pageout`, and `err_pageout` abort UPL ranges with error/free-on-empty semantics unless `UPL_NOCOMMIT` is set, then return `EINVAL` or `ENOTSUP`.
- `nop_searchfs` reports zero matches; block translation defaults store `(off_t)-1` or `(daddr64_t)-1` sentinel failure values.

Dependencies:
- Exposed by `vfs/vfs_support.h`; uses vnode interface argument types from `sys/vnode_if.h`, authorization types, `vn_revoke`, buffer write support, and UBC UPL abort routines.

Research notes:
- This file is fallback glue for vnode operation vectors. Its main importance is side-effect correctness, especially for UPL cleanup and output-parameter initialization.
- The `err_*` wrappers are not always pure error returns; callers relying on output values or cleanup must account for the paired `nop_*` behavior.
