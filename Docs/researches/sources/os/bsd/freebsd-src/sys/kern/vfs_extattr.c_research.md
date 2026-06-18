# File Research: sources/os/bsd/freebsd-src/sys/kern/vfs_extattr.c

## Role

Implements the FreeBSD extended-attribute syscall layer for VFS objects. It translates fd/path/link-oriented extattr syscalls into vnode operations (`VOP_SETEXTATTR`, `VOP_GETEXTATTR`, `VOP_DELETEEXTATTR`, `VOP_LISTEXTATTR`) and provides `extattrctl(2)` plumbing to the filesystem `VFS_EXTATTRCTL` method.

## Main Entry Points

- `sys_extattrctl()` resolves a target mount from `path`, optionally resolves and locks a backing `filename` vnode, starts a write section, and invokes `VFS_EXTATTRCTL()`.
- `sys_extattr_set_fd()`, `sys_extattr_get_fd()`, `sys_extattr_delete_fd()`, `sys_extattr_list_fd()` copy or construct arguments and dispatch to `kern_extattr_*_fd()`.
- `sys_extattr_set_file/link()`, `sys_extattr_get_file/link()`, `sys_extattr_delete_file/link()`, `sys_extattr_list_file/link()` differ mainly by `FOLLOW` vs `NOFOLLOW`.
- `kern_extattr_*_path()` variants accept a pathname segment type and are reusable by in-kernel callers.
- Internal helpers `extattr_set_vp()`, `extattr_get_vp()`, `extattr_delete_vp()`, and `extattr_list_vp()` implement the vnode operation common path.

## Behavior

Set operations validate `nbytes <= IOSIZE_MAX`, acquire write permission through `vn_start_write()`, lock the vnode exclusively, create a single-element userspace `uio`, run MAC checks when enabled, call `VOP_SETEXTATTR()`, and return bytes written through `td_retval[0]`.

Get operations lock the vnode shared. If the user data pointer is non-NULL, they pass a read `uio`; if it is NULL, they request only the attribute size via the `sizep` argument and return that size in `td_retval[0]`.

Delete operations start a write section, lock exclusively, run MAC checks, call `VOP_DELETEEXTATTR()`, and fall back to `VOP_SETEXTATTR(..., NULL, ...)` when delete is not supported by the filesystem.

List operations accept either a caller-supplied `uio` or NULL for size-only queries, lock shared, run MAC list checks, call `VOP_LISTEXTATTR()`, and return bytes listed or required size.

## Security And Capability Model

The fd paths use `getvnode_path()` with Capsicum rights specific to the operation: `CAP_EXTATTR_SET`, `CAP_EXTATTR_GET`, `CAP_EXTATTR_DELETE`, or `CAP_EXTATTR_LIST`. Path variants use `namei()` with audit vnode flags. MAC hooks gate set, get, delete, and list behavior when `MAC` is compiled in.

## Locking And Lifetime

Path lookup returns a referenced vnode; helpers operate on an unlocked vnode reference and handle vnode locking internally. `extattrctl()` carefully balances mount busying, write-start/write-finish, `filename_vp` lock handoff to `VFS_EXTATTRCTL()`, and final `vrele()`.

## Dependencies

This file is a syscall facade over the VFS vnode operation table. It depends on namei lookup, file descriptor capability lookup, audit annotation, MAC policy checks, vnode locking, and filesystem-specific extattr VOP implementations.

## Notes

The file is intentionally repetitive: fd, file path, and link path syscall wrappers share small differences in rights, path following, and argument copying. The actual semantic differences are concentrated in the four vnode helpers.
