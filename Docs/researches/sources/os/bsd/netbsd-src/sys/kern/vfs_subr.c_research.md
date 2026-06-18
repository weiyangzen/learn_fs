# File Research: sources/os/bsd/netbsd-src/sys/kern/vfs_subr.c

Read completely: 1856 lines.

Provides shared VFS support routines: vnode/buffer initialization, buffer invalidation and flushing, device vnode helpers, buffer-vnode association, syncer work queues, VFS sysctls, vnode diagnostics, statvfs helpers, timestamp/access-mode helpers, VFS operation wrappers, and DDB/debug printing.

Initialization and buffer/vnode helpers:
- `vntblinit()` initializes the syncer, mount subsystem, and vnode subsystem.
- `vinvalbuf()` flushes pages, optionally fsyncs, and invalidates all clean and dirty buffers for a locked vnode.
- `vtruncbuf()` frees pages and invalidates buffers at or beyond a logical block number.
- `vflushbuf()` pushes dirty pages and buffers, optionally waiting for output completion.
- `bdevvp()` and `cdevvp()` create deadfs-backed block or character device vnodes.
- `bgetvp()` attaches a busy buffer to a held vnode and places it on the clean buffer list.
- `brelvp()` detaches a buffer, updates syncer membership when no dirty buffers remain, and releases the vnode hold.
- `reassignbuf()` moves a buffer between clean and dirty vnode lists and schedules dirty vnodes on the syncer with file, directory, or metadata delay.
- `vfinddev()` and `vdevgone()` locate or revoke special-device vnodes.

Syncer subsystem:
- Defines delayed sync queues with `SYNCER_MAXDELAY`, per-vnode `VI_ONWORKLST`, and per-mount `IMNT_ONWORKLIST`.
- `vn_initialize_syncerd()` allocates sync queues, initializes the syncer lock, and installs `vfs.sync.*` sysctls.
- `vn_syncer_add_to_worklist()` and `vn_syncer_remove_from_worklist()` manage vnode sync work items.
- `vfs_syncer_add_to_worklist()` scatters mount sync slots to avoid all mounts syncing at once.
- `vfs_syncer_remove_from_worklist()` removes mount sync participation.
- `sched_sync()` is the syncer daemon: it lazily syncs eligible mounts with `VFS_SYNC(MNT_LAZY)`, processes expired vnode work items, tries nonblocking vnode references and locks, reschedules failures quickly, and paces work roughly once per second.
- SDT probes instrument syncer queue changes and sync attempts.

Sysctl and introspection:
- `sysctl_vfs_generic_fstypes()` returns registered filesystem type names.
- `sysctl_kern_vnode()` exports vnode pointer/value snapshots across all mounts.
- `vattr_null()` initializes `struct vattr` fields to `VNOVAL`.
- `vstate_name()`, `vprint_common()`, and `vprint()` format vnode state for diagnostics.
- DDB/debug helpers print buffers, vnodes, vnode locks, mounts, all mounts, and locked vnodes.

VFS metadata helpers:
- `vfs_getopsbyname()` looks up a registered filesystem operations table and increments its refcount.
- `copy_statvfs_info()` copies stable/statistical mount information into a `statvfs`.
- `set_statvfs_info()` fills mount-on and mount-from names from user or kernel strings, including chroot-relative mount path handling.
- `vfs_timestamp()` produces timestamps at configurable precision: seconds, HZ, microseconds, or nanoseconds.
- `vfs_unixify_accmode()` reduces rich access-mode bits to Unix-style checks, rejecting delete permissions that cannot be represented by mode/POSIX.1e ACLs.
- `setrootfstime()` records known root filesystem time.
- `vtype2dt()` maps vnode types to directory-entry `d_type` values.

VFS operation wrappers:
- `VFS_MOUNT()`, `VFS_START()`, `VFS_UNMOUNT()`, `VFS_ROOT()`, `VFS_QUOTACTL()`, `VFS_STATVFS()`, `VFS_SYNC()`, `VFS_FHTOVP()`, `VFS_VPTOFH()`, `VFS_SNAPSHOT()`, and `VFS_SUSPENDCTL()` call filesystem operations while taking the big kernel lock for non-MPSAFE mounts/vnodes.
- `VFS_MOUNT()` snapshots the MPSAFE state on entry because a mount operation may set `IMNT_MPSAFE`.
- `VFS_EXTATTRCTL()` unconditionally takes the kernel lock, with comments marking this as an SMP audit area.

Risks and notes:
- Buffer flushing depends on vnode locks, UVM object locks, `bufcache_lock`, and busy-buffer retry semantics; ordering mistakes can deadlock or lose delayed writes.
- Syncer membership uses vnode and mount flags plus separate queue locks; stale flags or missed removals can leave invalid queue state.
- `sched_sync()` accepts that vnodes can be recycled while syncing and rechecks queue heads accordingly.
- `sysctl_kern_vnode()` copies live vnode snapshots, useful for diagnostics but inherently race-sensitive.
- VFS wrappers assume operation vectors are valid for the mounted filesystem and encode legacy big-kernel-lock compatibility.
- `vfs_unixify_accmode()` intentionally collapses richer ACL semantics; callers must handle unsupported permissions separately.
