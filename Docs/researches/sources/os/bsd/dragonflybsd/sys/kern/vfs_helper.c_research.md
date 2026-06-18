# File Research: sources/os/bsd/dragonflybsd/sys/kern/vfs_helper.c

## Summary
Provides reusable helper routines for filesystem VOP implementations: UNIX permission checks, flag changes, create/chmod/chown semantics, and an optional VM-backed read shortcut.

## Main Responsibilities
- Implements standard access checking in `vop_helper_access()`.
- Implements inode flag update rules in `vop_helper_setattr_flags()`, including jail and securelevel handling.
- Provides create owner, chmod, and chown helpers for filesystems.
- Implements `vop_helper_read_shortcut()` to satisfy reads directly from valid resident VM pages when `LWBUF_IS_OPTIMAL`.

## Important Behavior
Write access is denied on read-only mounts for regular filesystem objects and denied for immutable files. UID 0 bypasses normal mode checks after those write restrictions. Chmod/chown helpers enforce privilege, group membership, sticky-bit, and SUID/SGID clearing rules.

The read shortcut avoids normal VOP read/buffer-cache paths only when a vnode has a VM object, a known file size, no `UIO_NOCOPY`, and fully valid resident pages. It uses `uiomove_nofault()` and falls back to normal read handling on faults or missing/invalid pages.

## Risks
Quota hooks are explicitly absent in `vop_helper_chown()`. The read shortcut depends on VM object/page state and is compiled to a no-op when `LWBUF_IS_OPTIMAL` is unavailable.
