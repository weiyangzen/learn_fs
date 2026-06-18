# File Research: sources/os/bsd/dragonflybsd/sys/kern/vfs_syscalls.c

## Role

This is the main VFS syscall implementation file. It translates user-visible filesystem syscalls into DragonFly's namecache, mount, vnode, VOP, and VFS operation layers. It contains mount/unmount, statfs/statvfs, path traversal state changes, file creation/removal/link/rename, attribute changes, timestamps, truncation, fsync, directory reading, filehandle operations, extended attributes, realpath, and posix fallocate.

## Main Responsibilities

- Mount lifecycle:
  - `sys_mount()` handles privilege/capability checks, user mounts, jail restrictions, module autoload, mount updates, new mount allocation, `VFS_MOUNT()`, mount-list insertion, root namecache setup, `checkdirs()`, syncer vnode allocation, and `VFS_START()`.
  - `sys_unmount()` resolves the target and calls `dounmount()`.
  - `dounmount()` serializes unmount, handles forced unmount process cleanup, syncs, stops/decommissions the syncer vnode, calls `VFS_UNMOUNT()`, tears down journals, vnode ops, namecache mount handles, credentials, mount refs, and notifies kqueue.
  - `vfs_unmountall()` is in `vfs_subr.c`, but its callback uses `dounmount()` from this file.
- Mount and filesystem control/statistics:
  - `sys_sync()`, `sync_callback()`
  - `sys_quotactl()`
  - `sys_mountctl()` and `kern_mountctl()`
  - `kern_statfs()`, `sys_statfs()`, `kern_fstatfs()`, `sys_fstatfs()`
  - `kern_statvfs()`, `sys_statvfs()`, `kern_fstatvfs()`, `sys_fstatvfs()`
  - `sys_getfsstat()` and `sys_getvfsstat()`
- Current/root directory changes:
  - `sys_fchdir()`, `kern_chdir()`, `sys_chdir()`
  - `kern_chroot()`, `sys_chroot()`, `sys_chroot_kernel()`
  - `checkvp_chdir()` validates directory and execute access.
  - `chroot_refuse_vdir_fds()` and `chroot_allow_open_directories` mitigate fchdir-based chroot escapes.
- Open and node creation:
  - `kern_open()`, `sys_open()`, `sys_openat()`
  - `kern_mknod()`, `sys_mknod()`, `sys_mknodat()`
  - `kern_mkfifo()`, `sys_mkfifo()`, `sys_mkfifoat()`
  - `kern_mkdir()`, `sys_mkdir()`, `sys_mkdirat()`
- Links, symlinks, rename, and deletion:
  - `kern_link()`, `sys_link()`, `sys_linkat()`
  - `kern_symlink()`, `sys_symlink()`, `sys_symlinkat()`
  - `sys_undelete()`
  - `kern_unlink()`, `sys_unlink()`, `sys_unlinkat()`
  - `kern_rename()`, `sys_rename()`, `sys_renameat()`
  - `kern_rmdir()`, `sys_rmdir()`
- Access, stat, pathconf, readlink:
  - `kern_access()`, `sys_access()`, `sys_eaccess()`, `sys_faccessat()`
  - `kern_stat()`, `sys_stat()`, `sys_lstat()`, `sys_fstatat()`
  - `sys_pathconf()`, `sys_lpathconf()`
  - `kern_readlink()`, `sys_readlink()`, `sys_readlinkat()`
- Attribute mutation:
  - `setfflags()`, `sys_chflags()`, `sys_lchflags()`, `sys_fchflags()`, `sys_chflagsat()`
  - `setfmode()`, `kern_chmod()`, chmod syscall variants
  - `setfown()`, `kern_chown()`, chown syscall variants
  - `getutimes()`, `getutimens()`, `setutimes()`, `kern_utimes()`, `kern_futimens()`, `kern_futimes()`, `kern_utimensat()`, and all utimes/futimes/utimens syscall variants.
- File size and persistence:
  - `kern_truncate()`, `sys_truncate()`
  - `kern_ftruncate()`, `sys_ftruncate()`
  - `kern_fsync()`, `sys_fsync()`, `sys_fdatasync()`
- Directory and descriptor utilities:
  - `kern_lseek()`, `sys_lseek()`
  - `kern_getdirentries()`, `sys_getdirentries()`, `sys_getdents()`
  - `sys_umask()`
- Revocation and NFS filehandles:
  - `sys_revoke()`
  - `sys_getfh()`
  - `sys_fhopen()`
  - `sys_fhstat()`
  - `sys_fhstatfs()`
  - `sys_fhstatvfs()`
- Extended attributes:
  - `sys_extattrctl()`
  - `sys_extattr_set_file()`
  - `sys_extattr_get_file()`
  - `sys_extattr_delete_file()`
- Path visibility and capability helpers:
  - `chroot_visible_mnt()`
  - `get_fscap()`
  - `sys___realpath()`
  - `kern_posix_fallocate()` and `sys_posix_fallocate()`

## Synchronization and Lifetime Model

- Name resolution is built around `struct nlookupdata` and `struct nchandle`; syscalls initialize lookup context, set flags such as `NLC_FOLLOW`, `NLC_CREATE`, `NLC_DELETE`, `NLC_REFDVP`, `NLC_SHAREDLOCK`, and then release through `nlookup_done()` or `nlookup_done_at()`.
- Vnode references and locks are handled explicitly through `cache_vget()`, `cache_vref()`, `vget()`, `vput()`, `vrele()`, `vn_lock()`, and `vn_unlock()`.
- Mount lifetime is protected through mount holds/drops, mount busy/unbusy, the mount list interlock, `mp->mnt_token`, and `mp->mnt_lock`.
- File descriptor operations use `holdfp()`, `holdvnode()`, `falloc()`, `fdalloc()`, `fsetfd()`, `fdrop()`, and `dropfp()`.
- Forced unmount scans all processes, drops matching text namecache handles, and may signal processes using the mount.
- Rename has extensive race handling: it tracks namecache generation counters, locks four namecache entries, retries on generation/ripout races, uses `mnt_renlock` for directory renames, and rejects mount point renames.

## Notable Design Details

- `sys_mount()` chooses capabilities based on filesystem type using `get_fscap()`, enforces jail restrictions for user mounts, prevents non-root NFS export, and silently adds `MNT_NOSUID | MNT_NODEV` for non-root mounts.
- Mount updates preserve previous `mnt_flag` and `mnt_kern_flag` so failed updates can roll back.
- `dounmount()` supports a quick-halt path for selected pseudo filesystems through `MNTK_QUICKHALT`.
- `checkdirs()` updates process current/root directories when a new filesystem is mounted over a directory already used by processes.
- Statfs paths are adjusted through `mount_path()` so chrooted processes see mount paths relative to their root.
- `getfsstat` and filehandle statfs paths filter mount visibility with `chroot_visible_mnt()`.
- `kern_open()` lets `vn_open()` replace the allocated file pointer, supports shared vnode locks where possible, and handles `O_EXLOCK`/`O_SHLOCK`.
- Hardlink restrictions are controlled by `security.hardlink_check_uid` and `security.hardlink_check_gid`.
- `kern_access()` and `kern_stat()` retry after `ESTALE` by forcing namecache re-resolution.
- `kern_fsync()` cleans VM pages first unless the mount has `MNTK_NOMSYNC`, then calls full or data-only VOP fsync and finally `buf_fsync()`.
- `sys_fhopen()` is explicitly protected by a restricted-root capability check because filehandle-to-open is a major security boundary.

## Cross-File Relationships

- Uses `vinvalbuf()`, `vfs_msync()`, `vcount()`, `vrevoke()`, `vfs_allocate_syncvnode()`, and many vnode helpers from `vfs_subr.c`.
- Uses syncer lifecycle and syncer vnode behavior from `vfs_sync.c`.
- Uses operation wrappers implemented in `vfs_vfsops.c` through `VFS_MOUNT()`, `VFS_START()`, `VFS_UNMOUNT()`, `VFS_STATFS()`, `VFS_STATVFS()`, `VFS_FHTOVP()`, `VFS_VPTOFH()`, and `VFS_EXTATTRCTL()`.
- Depends on VM coherency through `vfs_msync()`, vnode objects, and filesystem-specific VOP truncate/allocation behavior that may call into `vfs_vm.c`.

## Research Notes

- This file is the syscall boundary for most VFS behavior, so it combines user-copy validation, capability checks, path resolution, vnode locking, filesystem calls, and cleanup.
- The highest-risk areas are unmount teardown, rename races, chroot visibility/security, filehandle syscalls, mount update rollback, and descriptor/vnode reference ownership on error paths.
- The code heavily prefers shared `kern_*` helpers so classic syscalls and `*at` variants share semantics.
