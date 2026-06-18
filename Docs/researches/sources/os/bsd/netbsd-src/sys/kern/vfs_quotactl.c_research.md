# File Research: sources/os/bsd/netbsd-src/sys/kern/vfs_quotactl.c

Read completely: 194 lines.

Provides typed helper wrappers for the NetBSD quota-control VFS operation. Each function initializes a local `struct quotactl_args`, sets a specific `QUOTACTL_*` opcode, fills the relevant union fields, and dispatches through `VFS_QUOTACTL()`.

Covered operations:
- `vfs_quotactl_stat()` requests filesystem-wide quota status.
- `vfs_quotactl_idtypestat()` requests status for a quota id type.
- `vfs_quotactl_objtypestat()` requests status for a quota object type.
- `vfs_quotactl_get()` retrieves a quota value for a key.
- `vfs_quotactl_put()` writes a quota value for a key.
- `vfs_quotactl_del()` deletes quota data for a key.
- `vfs_quotactl_cursoropen()` and `vfs_quotactl_cursorclose()` manage quota iteration cursors.
- `vfs_quotactl_cursorskipidtype()`, `vfs_quotactl_cursorget()`, `vfs_quotactl_cursoratend()`, and `vfs_quotactl_cursorrewind()` wrap cursor traversal.
- `vfs_quotactl_quotaon()` and `vfs_quotactl_quotaoff()` enable or disable quotas by id type.

Risks and notes:
- This file performs no validation of ids, object types, paths, cursors, or buffers; validation is delegated to the filesystem `vfs_quotactl` implementation.
- All wrappers depend on the `struct quotactl_args` union layout matching each opcode exactly.
- Callers must provide correctly owned kernel pointers; these routines do not copy user memory.
- Locking and MPSAFE behavior are inherited from the `VFS_QUOTACTL()` wrapper in `vfs_subr.c`.
