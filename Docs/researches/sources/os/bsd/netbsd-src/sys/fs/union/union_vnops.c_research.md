# File Research: sources/os/bsd/netbsd-src/sys/fs/union/union_vnops.c

Read completely: 1974 lines.

Implements vnode operations for the legacy union filesystem. The operation table covers lookup, creation, whiteouts, copy-up-triggering open/access/setattr, I/O forwarding, mutation, directory iteration, lifecycle, locking, VM paging, kqueue filtering, and pass-through operations.

`union_lookup()` searches the upper layer first, respects whiteouts and opaque directories, then searches the lower layer as LOOKUP-only. It creates upper shadow directories for lower directories when needed and returns a union vnode over the resolved upper/lower pair. `union_parsepath()` asks both layers and returns the larger component consumption. `union_lookup1()` handles `..` across mount points and descends into mounted filesystems.

Write-oriented operations prefer or require the upper layer. `union_open()` copies lower regular files up on write opens, otherwise opens lower read-only and tracks `un_openl`; `union_access()` may copy up before write permission checks; and `union_setattr()` copies up lower regular files before changing attributes. `union_read()`, `union_write()`, `ioctl`, `poll`, `mmap`, `seek`, `readlink`, `pathconf`, `advlock`, `bmap`, `strategy`, `bwrite`, `getpages`, `putpages`, and `kqfilter` forward to the upper vnode when present or lower vnode otherwise, with extra locking for lower vnodes.

Namespace mutation is upper-layer based. `union_create()`, `union_mknod()`, `union_mkdir()`, and `union_symlink()` create in the upper layer and wrap results. `union_remove()` and `union_rmdir()` remove upper entries or create whiteouts for lower-only entries, using `union_check_rmdir()` for directories and `union_removed_upper()` after successful upper removal. `union_link()` copies lower regular files up before linking and has careful relookup logic to restore namei state after dropping locks. `union_rename()` delegates to upper vnodes and marks source whiteout when a lower vnode exists, but lower-only sources return `EXDEV` rather than being copied up.

Lifecycle and locking are customized. `union_inactive()` frees directory-cache references and recycles only uncached nodes. `union_reclaim()` transfers writecount back to the upper vnode and frees the union node. Locking follows the current `LOCKVP()` target, retrying if copy-up changes the lock target mid-operation. VM page operations require the union and underlying vnode to share the same object lock.

Risks and notes: `union_write()` panics if asked to write a non-special lower vnode without an upper; `union_remove()` and `union_rmdir()` panic if the parent lacks an upper vnode; `union_rename()` has an explicit comment that lower-only sources should be copied up but currently fail with `EXDEV`; revoke calls `vgone()` with an in-source uncertainty comment; kqueue filters stay attached to the layer chosen at registration even if copy-up later creates an upper vnode.
