# File Research: sources/os/bsd/openbsd-src/sys/kern/vfs_subr.c

Read completely: 2359 lines.

Provides broad shared VFS support: vnode table management, mount allocation/busying, vnode recycling, special-device aliasing, buffer-vnode association, buffer invalidation/flushing, sync/shutdown helpers, export helpers, access checks, sysctls, and DDB diagnostics.

Initialization and mount support:
- `vntblinit()` initializes vnode pools, vnode free/hold lists, `mountlist`, syncer queues, and NFS radix infrastructure when enabled.
- `vfs_mount_alloc()` allocates a busy mount, initializes refs and locks, links the covered vnode, copies VFS ops/type data, and applies default flags.
- `vfs_mount_take()`, `vfs_mount_free()`, and `vfs_mount_rele()` manage mount references and VFS type refcounts.
- `vfs_busy()` acquires the mount rwlock in read or write mode, fails if unmounting, and supports wait/nowait behavior.
- `vfs_unbusy()` releases the mount lock; `vfs_isbusy()` reports lock state.
- `vfs_rootmountalloc()` creates the root mount from a filesystem type and device name.
- `vfs_getvfs()` finds a mount by fsid, and `vfs_getnewfsid()` generates unique fsids.

Vnode allocation and references:
- `getnewvnode()` allocates or recycles vnodes based on `maxvnodes`, buffer-cache size, free lists, and hold lists.
- New vnodes initialize buffer trees, namecache trees, reverse-cache lists, operation vectors, type/tag, mount queue membership, and usecount.
- `insmntque()` moves vnodes between mount vnode lists.
- `vget()` obtains a use reference and optional lock, handling `VXLOCK` cleanup races and free-list removal.
- `vref()`, `vput()`, `vrele()`, `vhold()`, and `vdrop()` manage active and buffer-held vnode references.
- `vputonfreelist()` places inactive vnodes on the hold or free list and clears bio error state.

Special devices and aliases:
- `bdevvp()` and `cdevvp()` create block/character device vnodes through `getdevvp()`.
- `checkalias()` detects existing special-device aliases, flushes unused aliases, shares clone bitmaps, sets `VALIASED`, or reuses `VT_NON` block-device vnodes for cases such as root devices.
- `vfinddev()`, `vdevgone()`, and `vcount()` find, revoke, or count references to special-device vnodes across aliases.
- `vfs_mountedon()` checks whether a block device or alias is already a mount backing device.

Vnode flushing and reclamation:
- `vfs_mount_foreach_vnode()` iterates a mount's vnode list robustly against list mutation.
- `vflush()` applies `vflush_vnode()` to detect or force-close busy vnodes, optionally skipping system vnodes, clean vnodes, or non-writable regular files.
- `vclean()` drains vnode activity with `VXLOCK`, locks the vnode, terminates UVM state, optionally invalidates buffers and closes active vnodes, calls inactive/reclaim, purges namecache, switches to `dead_vops`, and wakes waiters.
- `vrecycle()`, `vgone()`, and `vgonel()` recycle or eliminate vnodes, detach mount membership, remove special-device aliases, purge special-device locks, and move bad vnodes to the front of the free list.

Buffer and I/O helpers:
- `vwaitforio()` waits for `v_numoutput` to reach zero.
- `vwakeup()` decrements output count and wakes waiters.
- `vinvalbuf()` optionally fsyncs a vnode, waits for I/O, invalidates clean/dirty buffers, writes delayed buffers if saving, and panics if buffers remain unexpectedly.
- `vflushbuf()` writes dirty buffers asynchronously or synchronously and waits for completion when requested.
- `bgetvp()` attaches a buffer to a vnode, takes a hold, and inserts it on the clean list.
- `brelvp()` detaches a buffer, removes syncer list membership when no dirty buffers remain, and drops the vnode hold.
- `buf_replacevnode()` changes a buffer's vnode association while adjusting outstanding output accounting.
- `reassignbuf()` moves buffers between clean and dirty vnode lists and schedules dirty vnodes on the syncer with shorter delays for directories and mounted block devices.

System sync, stall, and shutdown:
- `vfs_stall()` can freeze all mounts by taking write busy locks, syncing UVM/vnodes, calling `VFS_SYNC(MNT_WAIT)`, and marking mounts stalled; unstalls release those locks.
- `vfs_stall_barrier()` lets operations wait while global stalling is active.
- `vfs_unmountall()` traverses mounts in reverse order and force-unmounts them, retrying once on failures.
- `vfs_shutdown()` syncs, unmounts, quiesces softraid if present, and waits for buffers.
- `vfs_syncwait()` repeatedly calls `sys_sync()`, flushes lingering delayed-write buffers, reports busy counts, and gives up after bounded retries.

Access, exports, sysctl, and diagnostics:
- `vattr_null()` initializes vnode attributes to `VNOVAL`.
- `vaccess()` implements Unix owner/group/other permission checks, with root read/write bypass but execute requiring at least one execute bit for non-directories.
- `vnoperm()` checks mount `MNT_NOPERM`.
- `vfs_export()` and `vfs_export_lookup()` manage NFS export address lists when `NFSSERVER` is enabled.
- `vfs_sysctl()` exposes generic VFS data, filesystem config data with kernel pointers cleared, and buffer-cache statistics.
- Debug/DDB helpers print vnodes, buffers, mounts, locked vnodes, and statfs data.
- `copy_statfs_info()` copies stable mount stat fields and mount info into a caller's `statfs`.

Risks and notes:
- This file is a central lifetime manager; refcount, usecount, holdcount, mount-lock, and vnode-lock mistakes can cascade across VFS.
- `vclean()` and `vgonel()` depend on `VXLOCK`/`VXWANT` exclusion to avoid recycling races.
- Special-device alias handling is subtle, especially cloned character devices and root block-device vnodes.
- `vinvalbuf()` and `vfs_syncwait()` contain comments about difficult delayed-write and softdep interactions.
- `vfs_getvfs()` returns a raw mount pointer without taking a reference, so users must protect lifetime separately.
- Several paths assume `splbio()` around buffer/vnode list mutation.
