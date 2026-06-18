# File Research: sources/os/bsd/dragonflybsd/sys/kern/vfs_jops.c

## Summary
Implements the VOP shim layer for DragonFlyBSD’s mount-level VFS journaling. It attaches journal vnode operations to a mount, manages journal instances, and wraps mutating VOPs to emit redo and optional undo records.

## Main Responsibilities
- Handles `MOUNTCTL_*_VFS_JOURNAL` requests in `journal_mountctl()`.
- Attaches/detaches journal vnode ops and per-mount stream-id bookkeeping.
- Installs, restarts, removes, destroys, and reports status for per-mount journals.
- Builds per-operation `jrecord_list` transactions across all attached journals.
- Wraps mutating VOPs: setattr, write, putpages, ACL/extattr set, create, mknod, link, symlink, whiteout, remove, mkdir, rmdir, rename.

## Important Behavior
A mount may have multiple journals. `jreclist_init()` allocates a distinct stream id, creates one `jrecord` per journal, and reports whether any journal wants reversible undo data. `jreclist_done()` pops transaction records, commits or aborts based on VOP error, frees extra records, and releases the stream id.

Wrapped VOPs generally journal after the underlying filesystem operation succeeds. Reversible journals write undo data first for selected operations, such as write overwrite ranges, remove targets, rename overwrite targets, rmdir attributes, and setattr attributes. Redo records include credentials, paths, vnode references, vattrs, UIO data, page lists, or symlink payloads depending on operation.

## Risks
Several areas are explicitly partial: resync returns `EINVAL`, ACL redo/undo is mostly stubbed, extattr undo is not implemented, mmap modification handling is called out as unresolved, and hardlink/path identity handling has XXX notes. Append-write offset reconstruction is described as a hack. `journal_restart()` also has an explicit “XXX lock the jo” note.
