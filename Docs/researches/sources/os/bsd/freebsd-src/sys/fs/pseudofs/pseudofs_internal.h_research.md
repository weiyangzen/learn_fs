# File Research: sources/os/bsd/freebsd-src/sys/fs/pseudofs/pseudofs_internal.h

## Purpose

Defines private pseudofs internals shared by the core, vnode cache, fileno allocator, and vnode operations.

## Main Interface

`struct pfs_vdata` is per-vnode private data containing:
- `pvd_pn`: backing pseudofs node.
- `pvd_pid`: associated process id or `NO_PID`.
- `pvd_vnode`: back pointer.
- `pvd_hash`: vnode-cache hash link.

Declared internals:
- vnode cache load/unload/alloc/free.
- fileno init/uninit/alloc/free.
- `_vfs_pfs` sysctl declaration.

Debug macros:
- `PFS_TRACE()` and `PFS_RETURN()` emit operation tracing when `PSEUDOFS_TRACE` is enabled.

Inline wrappers:
- `pfs_lock()`, `pfs_unlock()`, and mutex assertions.
- `pn_fill()`, `pn_attr()`, `pn_vis()`, `pn_ioctl()`, `pn_getextattr()`, `pn_close()`, and `pn_destroy()` enforce expected callback presence, process lock state, and node lock state before invoking consumer callbacks.

## Integration Points

Included by pseudofs implementation files, not consumers. It bridges public callback definitions from `pseudofs.h` with internal vnode dispatch and lifecycle code.

## Risks and Review Notes

The inline wrappers encode several lock-state assertions. Violations in a consumer callback or vnode operation path will surface as kernel assertions under diagnostics, making these wrappers important correctness boundaries.
