# File Research: sources/os/bsd/openbsd-src/sys/kern/vfs_syscalls.c

Purpose: Implements OpenBSD VFS-related system calls and shared syscall helpers for mounting, path lookup operations, file creation/removal, attributes, descriptor operations, filesystem statistics, and positioned I/O.

Key behavior:
- `sys_mount()`, `sys_unmount()`, `dounmount()`, and `dounmount_leaf()` manage mount lifecycle, nested unmount collection, syncer vnode allocation/removal, `MNT_*` policy checks, unveil vnode cleanup, and mount-list mutation.
- `checkdirs()` retargets process current/root directories and `rootvnode` when a filesystem is mounted over an active directory.
- `sys_sync()`, `sys_quotactl()`, `sys_statfs()`, `sys_fstatfs()`, `sys_getfsstat()`, `sys_getfh()`, `sys_fhopen()`, `sys_fhstat()`, and `sys_fhstatfs()` expose filesystem sync, quota, stats, and file-handle operations.
- `sys_chdir()`, `sys_fchdir()`, `sys_chroot()`, `change_dir()`, `sys___realpath()`, and `sys_unveil()` integrate pathname resolution with current/root directory state, realpath generation, pledge, and unveil.
- `doopenat()` is the central open/openat implementation: allocates file descriptors, sets pledge/unveil access classes, calls `vn_open()`, handles `O_EXLOCK`/`O_SHLOCK`, local truncate-after-lock behavior, fd flags, and `UF_PLEDGEOPEN`.
- Node and name operations include `domknodat()`, `dolinkat()`, `dosymlinkat()`, `dounlinkat()`, `dorenameat()`, `domkdirat()`, and wrappers for mknod, mkfifo, link, symlink, unlink, rmdir, rename, and mkdir.
- Metadata syscalls include access/faccessat, stat/lstat/fstatat, pathconf/readlink, chflags/fchflags, chmod/fchmod, chown/lchown/fchown, utimes/utimens/futimens, truncate/ftruncate, fsync, getdents, umask, and revoke.
- `getvnode()` validates file descriptors as live vnode-backed files; pread/preadv/pwrite/pwritev build `uio`s and delegate to generic file read/write vector helpers.

Security and policy:
- Enforces root checks for mount, unmount, file handles, chroot, privileged mknod, and device creation.
- Uses pledge promise bits and unveil permissions on namei paths throughout, including read/write/create/delete/attribute/chown classes.
- Hides filesystem IDs and generation numbers from non-root callers for NFS security.
- Blocks unsafe mount flag combinations such as `MNT_NOPERM` without `MNT_NODEV|MNT_NOEXEC`.

Important dependencies:
- VFS entry points: `VFS_MOUNT`, `VFS_UNMOUNT`, `VFS_ROOT`, `VFS_SYNC`, `VFS_STATFS`, `VFS_FHTOVP`, `VFS_VPTOFH`, `VFS_START`.
- Vnode entry points: `VOP_ACCESS`, `VOP_SETATTR`, `VOP_MKNOD`, `VOP_LINK`, `VOP_SYMLINK`, `VOP_REMOVE`, `VOP_RENAME`, `VOP_MKDIR`, `VOP_RMDIR`, `VOP_READDIR`, `VOP_READLINK`, `VOP_FSYNC`, `VOP_REVOKE`.
- File descriptor layer: `falloc`, `fdinsert`, `fdremove`, `fd_getfile`, `getvnode`, `closef`, `FRELE`.
