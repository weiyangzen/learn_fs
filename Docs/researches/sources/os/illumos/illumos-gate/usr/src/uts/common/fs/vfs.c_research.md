# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/vfs.c

## Purpose
`vfs.c` is the illumos kernel’s core VFS mount/filesystem-instance manager. It owns VFS operation-vector construction, root filesystem mounting, common mount/unmount paths, mount option parsing, VFS list/hash management, filesystem switch lookup/loading, VFS reference lifetime, mount-table timestamps/events, VFS feature bits, and lofi-backed file mounts.

## Major Responsibilities
- Provides `fsop_*` dispatch wrappers for VFS operations: mount, unmount, root, statvfs, sync, vget, mountroot, freefs, vnstate, syncfs.
- Builds `vfsops_t` vectors from filesystem templates through `fs_copyfsops()` and shared `fs_build_vector()`.
- Initializes global VFS state in `vfsinit()`, including the VFS kmem cache, vnode cache, FEM, stray/EIO VFS ops, built-in filesystem init, vopstats startup, xattrs, and reparse support.
- Mounts the root filesystem in `vfs_mountroot()` and then mounts required early filesystems such as `/devices`, `/dev`, `ctfs`, `proc`, `mntfs`, `tmpfs`, `objfs`, `bootfs`, and global-zone `sharefs`.
- Implements `domount()`, the central common mount path used by syscall/autofs/NFS trigger/PxFS callers.
- Implements `dounmount()` and `vfs_unmountall()` for individual and shutdown unmount flows.
- Maintains the global circular VFS list, per-zone VFS lists, and fsid hash buckets.
- Maintains `/etc/mnttab` change timestamps, polling wakeups, and dummy vnode operations for file-event notification.
- Manages mount option tables, option cancellation, tags, parsing, stringification, copying, merging, and freeing.
- Manages `vfssw` lookup/autoload/reference counts and `vfs_t` allocation/reference lifecycle.
- Supports VFS feature bit registration/query/propagation.
- Supports file-backed filesystem mounting by automatically mapping eligible regular files through `lofi`.

## Key Data and Globals
- `rootdir`, `devicesdir`, `devdir`: global root/device vnodes.
- `rootvfs`: root VFS and global circular VFS list anchor.
- `rvfs_list`, `vfshsz`: VFS fsid hash table and bucket count.
- `vfslist`: global VFS list/mnttab lock.
- `vfssw_lock`: filesystem switch table lock.
- `vfs_miplist`: mount-in-progress device list used to detect concurrent device mounts.
- `vfs_mnttab_ctime`, `vfs_mnttab_mtime`, `vfs_pollhd`, `vfs_mntdummyvp`: mnttab event state.
- `vfs_mntopts`: generic VFS option prototype covering `ro/rw`, `suid/nosuid`, `devices/nodevices`, `setuid/nosetuid`, `nbmand/nonbmand`, `exec/noexec`, and `remount`.

## Mount Flow
`domount()` is the central function. It:
- Marks the mountpoint vnode with `VVFSLOCK`.
- Resolves the filesystem type from explicit `fsname`, string options, numeric fstype, or rootfs default.
- Holds and validates the `vfssw` entry, checks `VFS_INSTALLED`, and applies `secpolicy_fs_allowed_mount()`.
- Copies prototype mount options, parses option strings, and lets flag bits override option state.
- Validates remount support, read-only transitions, and NBMAND immutability on remount.
- Resolves resource and mountpoint paths, including non-global-zone rootpath expansion.
- Locks the mountpoint with `vn_vfswlock()` unless `MS_NOSPLICE` is used.
- Allocates or reuses a `vfs_t`, initializes ops, holds it, optionally creates a lofi mapping, and applies forced `nosuid` for lofi mounts.
- Adds device mounts to the mount-in-progress list before calling the filesystem.
- Swaps final option tables into `vfsp`, sets resource/mountpoint strings, emits mounted-over events, and calls `VFS_MOUNT()`.
- On success, updates VFS flags from options, builds the returned option string, initializes vopstats, links into the namespace with `vfs_add()` or holds an unspliced VFS, and returns the held `vfsp`.
- On failure, restores remount state, removes lofi/mip state, unlocks, frees partial VFS/mnttab data, and unreferences the `vfssw`.

## Root and Boot Integration
- `vfs_mountroot()` initializes locks/hash structures, calls `rootconf()`, establishes `rootdir`, sets early process cwd/root, records the global zone root vnode, enables module root access, initializes ZFS boot support, sets root resource info, and mounts required pseudo filesystems.
- `rootconf()` chooses and loads the root filesystem module, handles x86 HVM boot hooks, cluster boot hooks, NFS/iSCSI boot plumbing, initializes `rootvfs`, mounts root read-only first, and records `rootdev`.
- `getrootfs()` derives root filesystem type/module from boot properties, including special NFS type mapping and ZFS bootfs detection.

## VFS Lists, Hashing, and Locking
- `vfs_add()` attaches a mounted VFS to the covered vnode, sets flags, holds references, and calls `vfs_list_add()`.
- `vfs_list_add()` assigns creation time, zone ownership/ref, inserts into global list, zone list, fsid hash, updates mnttab time, and wakes mnttab pollers.
- `vfs_list_remove()` removes from hash/global/zone lists and updates mnttab state.
- `getvfs()` looks up by `fsid_t` through the hash table and returns a held VFS.
- `vfs_lock()`, `vfs_rlock()`, `vfs_lock_wait()`, `vfs_rlock_wait()`, and `vfs_unlock()` use the shared vnode/VFS lock table implemented in `vnode.c`.
- `vfs_lock_held()` and `vfs_lock_owner()` expose lock diagnostics.

## Mount Options
- Option tables are deep-copied and freed with `vfs_copyopttbl*()` and `vfs_freeopttbl()`.
- `vfs_parsemntopts()` destructively scans comma-separated option strings, supports `key=value`, and can create dynamic option slots.
- `vfs_setmntopt_nolock()` handles value allocation, display flags, `MO_IGNORE`, `VFS_CREATEOPT`, and cancellation lists.
- `vfs_buildoptionstr()` serializes set options back to a comma-separated string.
- `vfs_mergeopttbl()` merges outer/global and inner/filesystem option tables while preserving cancel semantics.
- `vfs_settag()` and `vfs_clrtag()` let privileged callers add/remove arbitrary tag options on a mounted filesystem identified by dev and mountpoint.

## Unmount and Shutdown
- `dounmount()` purges DNLC entries, syncs unless forced, locks the VFS, calls `VFS_UNMOUNT()`, tears down vopstats, removes namespace linkage, unlocks covered vnode, and releases references.
- `vfs_unmountall()` walks the list backwards during shutdown, syncs and unmounts non-root filesystems, and restarts traversal safely if the list changed while unlocked.
- `vfs_syncall()` performs shutdown sync, then loops on dirty buffer/page counts with progress detection and retry limits.

## Filesystem Switch and Operation Vectors
- `allocate_vfssw()` reserves a `vfssw` entry before root is fully available.
- `vfs_getvfssw()` maps public fstype to module name, autoloads modules, and returns a referenced switch entry.
- `vfs_getvfsswbyname()` and `vfs_getvfsswbyvfsops()` search existing entries.
- `vfs_refvfssw()` / `vfs_unrefvfssw()` maintain unload-prevention counts.
- `fs_build_vector()` is the generic vector builder used by both VFS and vnode layers; it maps named operation definitions into fixed vectors, substitutes `fs_default`/`fs_error`, rejects NULL funcs, and reports unused supplied ops.

## Integration Points
- Calls into vnode layer for mountpoint locking, vnode allocation, dummy vnode ops, mounted-over events, and path setting.
- Calls into filesystem modules through `VFS_*` operation vectors.
- Interacts with zones through path translation, `zone_find_by_path()`, `mount_in_progress()`, and VFS zone refs.
- Integrates with DNLC, lofi/LDI, boot properties, ZFS SPA boot, cluster boot, mntfs polling, kstats/vopstats, FEM, xattrs, and reparse points.

## Risks and Invariants
- `domount()` has many partial-initialization exits; correctness depends on paired cleanup for option tables, vnode holds, lofi mappings, mip entries, VFS holds, and locks.
- VFS list updates must hold `vfslist`; hash bucket locking order is list lock before hash lock.
- Mnttab-visible fields must not become NULL while a listed VFS is being remounted.
- Non-global-zone resource/mountpoint expansion must stay below `MAXPATHLEN`.
- `vfs_delmip()` returns without unlocking if the entry is unexpectedly absent; the code comments say this should not happen, but this path would leave `vfs_miplist_mutex` held.
- Lofi mounts are deliberately restricted from remount/global/suid/setuid/devices options and force `nosuid`.
- `VFS_RELE()` calls filesystem `VFS_FREEVFS()` only after successful full initialization; partial mount failures use `vfs_free()` directly.
