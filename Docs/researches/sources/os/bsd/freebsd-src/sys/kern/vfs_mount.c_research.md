# File Research: sources/os/bsd/freebsd-src/sys/kern/vfs_mount.c

## Role

Implements the general mount and unmount subsystem: user-facing `nmount(2)` and legacy `mount(2)`, kernel mount argument construction, mount option parsing and sanitization, mount structure allocation/destruction, update/remount handling, unmount and deferred recursive unmount, mount reference accounting, and mount event notification.

## Main Entry Points

- `sys_nmount()` validates iovec count, filters `MNT_ROOTFS`, builds a `uio`, and calls `vfs_donmount()`.
- `sys_mount()` implements the older API by building mount arguments and calling filesystem `vfs_cmount`.
- `vfs_donmount()` parses and sanitizes option vectors, derives mount flags, handles export-only jail updates, optional auto-readonly retry, and dispatches to `vfs_domount()`.
- `vfs_domount()` resolves the mount path and chooses first mount vs update.
- `vfs_domount_first()` performs a new mount over a vnode.
- `vfs_domount_update()` updates flags, options, exports, and read/write state on an existing mount.
- `sys_unmount()` and `kern_unmount()` resolve target mount and call `dounmount()`.
- `dounmount()` performs the actual unmount and destruction sequence.
- `kernel_mount()` supports in-kernel mounts using accumulated `struct mntarg` arguments.

## Mount Option Handling

`vfs_buildopts()` copies name/value iovec pairs into a `vfsoptlist`, enforces `VFS_MOUNTARG_SIZE_MAX`, requires NUL-terminated option names, and sanitizes duplicates. `vfs_sanitizeopts()` keeps the last occurrence, with special equivalence for `no` prefixes and read-only/read-write aliases.

`vfs_donmount()` recognizes global options such as `update`, `force`, `reload`, `async`, `noatime`, `noexec`, `nosuid`, `nosymfollow`, `ro`, `rw`, `autoro`, `union`, `export`, `automounted`, `nocover`, and `emptydir`. It also keeps `errmsg` copyout behavior aligned with the original option position.

Public helpers include `vfs_filteropt()`, `vfs_getopt()`, `vfs_getopts()`, `vfs_getopt_pos()`, `vfs_getopt_size()`, `vfs_flagopt()`, `vfs_scanopt()`, `vfs_setopt()`, `vfs_setopt_part()`, `vfs_setopts()`, and `vfs_copyopt()`.

## Mount Lifecycle

`vfs_mount_alloc()` initializes a UMA-allocated `struct mount`, vfs operations, statfs identity, mount credential, hash seed, upper-mount lists, and MAC label state. `vfs_domount_first()` validates permissions and covered vnode suitability, marks `VI_MOUNT`, calls `VFS_MOUNT()`, `VFS_STATFS()`, and `VFS_ROOT()`, installs `VIRF_MOUNTPOINT` and `v_mountedhere`, inserts the mount into `mountlist`, fires mount event handlers/devctl, updates process directories, and allocates a sync vnode for writable mounts.

`vfs_domount_update()` requires a root vnode, checks privilege or jail export rules, busies the mount, sets update flags, merges options, optionally calls `VFS_MOUNT()`, processes export structures across old and current ABI layouts, restores flags on failure, updates statfs/options, and toggles the sync vnode for read/write transitions.

`vfs_mount_destroy()` drains references, verifies no dangling vnodes or upper registrations remain, releases covered vnode, options, export state, vfsconf reference, MAC state, credentials, and returns the structure to the UMA zone.

## Unmount Lifecycle

`kern_unmount()` supports lookup by FSID or path, rejects recursive/deferred flags from userspace, checks privilege and MAC policy, refuses root unmount, and calls `dounmount()`.

`dounmount()` supports forced and recursive unmount. Recursive forced unmounts enqueue upper mounts through the deferred taskqueue and wait for uppers to drain when needed. The main unmount sequence locks the covered vnode, enters the VFS operation barrier, starts a write drain, marks `MNTK_UNMOUNT`, clears cached root, optionally checks use counts, purges on force, drains lock refs, flushes with `vfs_periodic()`, deallocates the sync vnode, calls `VFS_UNMOUNT()`, removes the mount from `mountlist`, clears mountpoint state, fires unmount notifications, handles root globals, and destroys the mount.

Deferred unmount state is controlled by sysctls under `vfs.deferred_unmount`, with retry limit, retry delay, and total retry counters.

## Reference And Operation Accounting

`vfs_ref_from_vp()`, `vfs_ref()`, and `vfs_rel()` use per-CPU mount counters when safe and fall back to the mount interlock otherwise. `vfs_op_enter()` drains per-CPU counters into stable mount counters and establishes a barrier for operations that need stable accounting. Diagnostic helpers can assert and dump counter state.

Upper/lower stacked mount relationships are managed by `vfs_register_upper_from_vp()`, `vfs_register_for_notification()`, `vfs_unregister_for_notification()`, and `vfs_unregister_upper()`.

## Kernel Mount Argument API

`mount_arg()`, `mount_argf()`, `mount_argsu()`, and `mount_argb()` accumulate iovec name/value pairs in `struct mntarg`; `kernel_mount()` converts them into a sysspace `uio`, calls `vfs_donmount()`, and frees all allocations.

## Additional Utilities

`__vfs_statfs()` normalizes statfs fields before calling the filesystem method. `vfs_mountedfrom()` sets `f_mntfromname`. `mount_devctl_event()` publishes mount/remount/unmount events. `vfs_remount_ro()` force-remounts a busied mount read-only. `suspend_all_fs()` and `resume_all_fs()` suspend/resume writable local filesystems, and `vfs_exjail_clone()` clones export jail credentials.

## Dependencies

This file ties together namei lookup, filesystem registration, vnode mountpoint flags, syncer vnode management, MAC hooks, jail/prison policy, NFS export structures, GEOM-root interactions through callers, taskqueues, event handlers, devctl, per-CPU counters, and filesystem `VFS_*` operations.

## Notes

This is the main policy and lifecycle center for FreeBSD mount state. Its correctness depends on strict lock ordering around covered vnodes, mount interlocks, operation barriers, and option ownership transfer between caller lists and `mp->mnt_opt`.
