# File Research: sources/os/bsd/netbsd-src/sys/kern/vfs_syscalls.c

Read completely: 5056 lines.

## Purpose
Implements NetBSD's main VFS-facing system calls: mount/unmount, filesystem statistics, quotas, cwd/root changes, open/openat, file handles, node creation, links, unlink/rmdir, lseek and positional I/O wrappers, access/stat/pathconf/readlink, metadata updates, timestamps, truncation, fsync variants, rename, directory reads, umask, revoke, fallocate, and discard.

## Main Interfaces
- Mount lifecycle: `sys___mount50`, `do_sys_mount`, `mount_update`, `mount_getargs`, `sys_unmount`, `do_sys_sync`, `sys_sync`, `vfs_syncwait`.
- Quotas/statfs: `sys___quotactl`, `do_sys_quotactl`, `dostatvfs`, `do_sys_pstatvfs`, `do_sys_fstatvfs`, `do_sys_getvfsstat`.
- Directory context: `do_sys_fchdir`, `sys_fchdir`, `sys_fchroot`, `do_sys_chdir`, `sys_chdir`, `sys_chroot`, `change_root`, `chdir_lookup`.
- Open and file handles: `do_open`, `fd_open`, `do_sys_openat`, `sys_open`, `sys_openat`, `vfs_composefh*`, `vfs_fhtovp`, `vfs_copyinfh_alloc`, `sys___getfh30`, `dofhopen`, `do_fhstat`, `do_fhstatvfs`.
- Namespace operations: `do_sys_mknodat`, `do_sys_mkfifoat`, `do_sys_linkat`, `do_sys_symlinkat`, `do_sys_unlinkat`, `do_sys_renameat`, `do_sys_mkdirat`, `sys_rmdir`.
- File operations: `sys_lseek`, `sys_pread`, `sys_preadv`, `sys_pwrite`, `sys_pwritev`, `sys___getdents30`.
- Metadata and storage: `do_sys_accessat`, `do_sys_statat`, `kern_pathconf`, `do_sys_readlinkat`, `change_flags`, `change_mode`, `change_owner`, `do_sys_utimensat`, `do_sys_utimes`, `sys_truncate`, `sys_ftruncate`, `sys_fsync`, `sys_fsync_range`, `sys_fdatasync`, `dorevoke`, `sys_posix_fallocate`, `sys_fdiscard`.

## State And Control Flow
The file is the syscall glue between user ABI arguments and vnode/VFS operations. It copies user paths into `pathbuf`, builds `nameidata`, handles `*at` directory-file-descriptor roots through `fd_nameiat`, obtains vnode references, performs authorization through kauth, locks vnodes where required, dispatches `VOP_*` or `VFS_*`, then releases references and descriptor holds.

Mount paths resolve the covered vnode, obtain or autoload `vfsops`, stage mount data from userspace, and route to getargs, update, or new mount. Successful mount/unmount submits `EVFILT_FS` notifications through `fs_klist`.

Open allocates a file descriptor first, calls `vn_open`, handles special `EDUPFD`/`EMOVEFD` cases, attaches `vnops`, optional advisory locks, close-on-exec/fork flags, and finally affixes the descriptor.

Rename is notably complex. It starts an fstrans transaction on the source mount, performs source and target lookups, rejects `.`/`..`, enforces same-mount renames, enters the VFS rename lock, relookups the target under the legacy `VOP_RENAME` protocol, applies directory/type checks, handles POSIX retain semantics, optionally checks veriexec, and then delegates ownership of vnode references to `VOP_RENAME`.

## Dependencies And Integration
Depends on path/namei, file descriptor tables, vnode operations, mount/vfs operations, fstrans, kauth, kqueue `EVFILT_FS`, quota APIs, NFS filehandle formats, veriexec hooks, fileassoc hooks, ktrace, syncer worklists, stat/statvfs buffers, and generic fileops from `sys_generic.c`.

## Risks And Edge Cases
- The `VOP_RENAME` path carries many comments about legacy locking protocol weaknesses; it acknowledges stale vnode identity races and relies on filesystem-side behavior.
- `fd_nameiat` uses path string inspection to decide whether `fdat` matters; absolute paths ignore the directory fd.
- Mount updates suspend the filesystem, mutate mount flags tentatively, and must restore flags and worklist membership on failure.
- Filehandle import supports padded NFSv2 handles and validates size consistency; privileged filehandle syscalls can bypass pathname lookup.
- `access` can substitute real IDs unless `AT_EACCESS` is requested, which differs from normal effective-credential checks.
- Timestamp code handles `UTIME_NOW`, `UTIME_OMIT`, null-time semantics, and birthtime adjustment when mtime predates birthtime.
- `posix_fallocate` returns errors through `retval` and syscall success status, matching POSIX's unusual error-return convention.

## Filesystem Relevance
Central. This is NetBSD's syscall-to-VFS front door for mounted filesystem management, pathname namespace mutation, vnode-backed file creation/opening, metadata mutation, synchronization, and storage allocation/deallocation.
