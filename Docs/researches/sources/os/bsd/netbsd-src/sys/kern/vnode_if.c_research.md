# File Research: sources/os/bsd/netbsd-src/sys/kern/vnode_if.c

Read completely: 2381 lines.

Generated vnode operation front-end wrappers. The file should not be edited directly; it is generated from `vnode_if.src` by `vnode_if.sh`.

Common wrapper behavior:
- Each `VOP_*` wrapper fills an operation-specific argument structure, calls `vop_pre()`, dispatches through `VCALL(vp, VOFFSET(...), &a)`, and calls `vop_post()`.
- `vop_pre()` takes the big kernel lock for non-`VV_MPSAFE` vnodes and starts filesystem transactions according to the generated `FST_*` mode.
- `vop_post()` ends filesystem transactions for normal/lazy modes and releases the big kernel lock when acquired.
- `VOP_LOCK()` and `VOP_UNLOCK()` have special fstrans handling to match lock acquisition/release semantics.
- Optional `VNODE_LOCKDEBUG` assertions check whether vnode arguments are expected to be unlocked, locked, or exclusively locked.

Vnode operation descriptors:
- Defines `vop_default_desc` and one `vnodeop_desc` per operation.
- Descriptor metadata includes operation offset, printable name, vnode argument offsets, optional output vnode pointer offset, credential offset, componentname offset, and WILLRELE/WILLPUT flags.
- The final `vfs_op_descs[]` table lists all descriptors with default first and NULL terminator.

Covered operations:
- File and directory operations include lookup, create, mknod, open, close, access/accessx, getattr/setattr, read/write, fallocate/fdiscard, fsync, seek, remove, link, rename, mkdir, rmdir, symlink, readdir, readlink, abortop, inactive, reclaim, bmap, strategy, pathconf, advlock, whiteout, getpages, and putpages.
- ACL wrappers cover get/set/check ACL.
- Extended attribute wrappers cover open/close/get/list/delete/set extended attributes.
- Polling, kqueue filter, revoke, mmap, ioctl, fcntl, print, and islocked wrappers are also generated.

Kqueue notification glue:
- Post hooks emit vnode knotes for create, mknod, setattr, ACL changes, link, mkdir, remove, rmdir, symlink, open, close, read, and write.
- Write and setattr hooks compare old size/offset to detect `NOTE_EXTEND`.
- Remove/rmdir special handling may hold the target vnode before the operation so notifications can still be delivered after filesystem code drops references.
- Close notifications suppress meaningless `NOTE_CLOSE` on already-dead/revoked vnodes.

Risks and notes:
- Correctness depends on the generator and `vnode_if.src`; local edits here are disposable.
- Generated lock assertions are diagnostic-only and not complete locking proof.
- The fstrans retry loop handles mount changes across transaction start, but each wrapper's selected `FST_*` mode must match operation semantics.
- Knote post hooks deliberately run after `vop_post()` to reduce time under the big kernel lock.
