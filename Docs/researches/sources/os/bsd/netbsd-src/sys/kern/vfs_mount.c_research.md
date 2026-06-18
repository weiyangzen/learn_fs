# File Research: sources/os/bsd/netbsd-src/sys/kern/vfs_mount.c

Read completely: 1729 lines.

Implements mount structure allocation, reference/busy management, mount list iteration, vnode iteration by mount, vnode flushing, mount and unmount orchestration, root filesystem mounting, per-mount specific data, and mounted-device checks.

Global mount state:
- Defines `rootvnode`, the global mount list, mount-list lock, VFS list lock, mount-specific data domain, mount id lock, and generation counter.
- `vfs_mount_sysinit()` initializes mount list infrastructure and mount-specific data support.
- `vfs_mountalloc()` allocates and initializes `struct mount`, mutex objects, vnode list, lower-level transaction state, specific data, and generation number.
- `vfs_rootmountalloc()` finds a filesystem type, allocates a root mount, marks it read-only initially, fills root mount names, and busies the mount.

Reference and busy lifecycle:
- `vfs_getnewfsid()` builds a unique fsid from filesystem type and a mount counter, checking existing mounts directly under `mountlist_lock`.
- `vfs_getvfs()` locates a mount by fsid using the iterator; a comment notes it should add a reference.
- `vfs_ref()` and `vfs_rele()` manage atomic mount references; final release tears down specific data, mutexes, vfsops reference, and filesystem transaction state.
- `vfs_busy()`/`vfs_trybusy()` start filesystem transactions, reject gone mounts, and take an extra mount reference.
- `vfs_unbusy()` ends the transaction and drops that reference.
- `vfs_set_lowermount()` swaps stacked/lower mount references, rejecting the dead root mount and using busy/ref protection.

Vnode list and flushing:
- `vfs_vnode_iterator_init/destroy/next()` implement marker-based iteration over a mount’s vnode list, avoiding unstable traversal while vnodes are reclaimed.
- `vfs_insmntque()` moves a vnode between mount vnode lists and donates/releases mount references accordingly.
- `vflush()` repeatedly walks vnodes, flushes deferred releases, and calls `vflush_one()` until busy vnodes are gone or retries are exhausted.
- `vflush_one()` skips selected/system vnodes, handles `WRITECLOSE` filtering, fsync/getattr checks, tries recycling, and forcibly kills or anonymizes vnodes under `FORCECLOSE`.

Mount path:
- `mount_domount()` authorizes a new mount, rejects non-directory mount points and unsupported exported-new-mount flags, allocates a mount, calls `VFS_MOUNT()`, suspends the new filesystem, validates the mount point path with `namei()`, invalidates buffers on the covered vnode, appends the mount to the global list, adds it to the syncer when appropriate, links `v_mountedhere`, updates process cwd/root references through `mount_checkdirs()`, runs `VFS_STATVFS()` and `VFS_START()`, and optionally starts extended attributes.
- Error cleanup force-unmounts a freshly mounted filesystem, resumes if needed, clears lower mount state, and releases the mount.

Unmount and shutdown:
- `dounmount()` checks veriexec, suspends the filesystem if needed, marks unmount in progress, clears async writes temporarily, purges namecache entries, removes syncer state, syncs unless forced/read-only, calls `VFS_UNMOUNT()`, marks `IMNT_GONE`, detaches the covered vnode, resumes, removes the mount list entry, asserts no dangling vnodes, calls unmount hooks, clears lower mount, and releases mount/covered vnode references.
- `vfs_unmount_next()` chooses mounts by descending generation to unmount newer/stacked filesystems first.
- `vfs_unmount_forceone()` and `vfs_unmountall1()` provide forced and full unmount passes.
- `vfs_sync_all()` suspends scheduling, performs sync, and waits for the syncer before shutdown.
- `vfs_shutdown()` syncs and unmounts unless the kernel has panicked.

Root mounting and utilities:
- `vfs_mountroot()` validates the root device class, opens disk root devices, honors a configured root filesystem type or tries all registered root-capable filesystems, marks the root mount, obtains `/`, initializes process cwd state, and enables module loading from VFS.
- Mount-specific data helpers wrap the `specificdata` API.
- `vfs_mountedon()` and `rawdev_mounted()` detect mounted block devices or corresponding raw character devices.
- `makefstype()` derives a compact numeric filesystem type from a name.
- Mount-list iterators use marker entries and busy mounts while yielding them to callers.
- `_mountlist_next()` is an unlocked DDB-only traversal helper.

Risks and notes:
- The file’s correctness depends on disciplined ownership of mount references, busy counts, filesystem transactions, and vnode references.
- `vfs_getvfs()` is documented as lacking a mount reference, so consumers must be careful about lifetime.
- Unmount failure paths restore async and syncer state and may restart extattrs, which is easy to regress.
- Successful unmount panics on dangling vnodes, making filesystem reclaim behavior part of the contract.
- `rawdev_mounted()` has an explicit limitation: it checks a specific slice, not all slices on the same disk.
- Marker-based mount and vnode iterators are central to avoiding list corruption during concurrent mutation.
