# File Research: sources/os/bsd/freebsd-src/sys/kern/vfs_syscalls.c

Primary syscall front-end for FreeBSD VFS operations. It translates user-visible filesystem syscalls into namei lookups, vnode operations, mount operations, Capsicum right checks, MAC/audit hooks, jail visibility rules, and compatibility ABI conversions.

Key responsibilities:
- Filesystem-wide operations: `kern_sync()`, `sys_quotactl()`, `kern_statfs()`, `kern_fstatfs()`, `kern_getfsstat()`, plus FreeBSD 4/11 statfs conversion paths.
- Directory/root context: `kern_chdir()`, `kern_chroot()`, `sys_fchdir()`, `sys_fchroot()`, and `change_dir()`, including `unprivileged_chroot` policy and `NO_NEW_PRIVS` requirement.
- Open/create namespace operations: `kern_openat()`, `kern_openatfp()`, `kern_mknodat()`, `kern_mkfifoat()`, `kern_linkat()`, `kern_symlinkat()`, `kern_funlinkat()`, `kern_frmdirat()`, `kern_renameat()`, `kern_mkdirat()`.
- Metadata syscalls: `kern_statat()`, `kern_accessat()`, `kern_chflagsat()`, `kern_fchmodat()`, `kern_fchownat()`, `kern_utimesat()`, `kern_utimensat()`, `kern_truncate()`, `kern_fsync()`.
- Directory and descriptor helpers: `kern_getdirentries()`, `getvnode_path()`, `getvnode()`, `sys_umask()`, `sys_revoke()`.
- File-handle operations for NFS/lockd-style privileged access: `kern_getfhat()`, `kern_fhopen()`, `kern_fhstat()`, `kern_fhstatfs()`, `kern_fhlinkat()`, `sys_fhreadlink()`.
- Advisory/copy helpers: `kern_posix_fadvise()` stores or applies per-file advice, and `kern_copy_file_range()` validates descriptors, offsets, ranges, and delegates to `vn_copy_file_range()`.

Important patterns:
- `at2cnpflags()` is the central translator from `AT_*` lookup flags to namei flags such as `FOLLOW`, `NOFOLLOW`, `RBENEATH`, and `EMPTYPATH`.
- Most mutating path operations use `NDPREINIT`, `bwillwrite()`, `vn_start_write()`, VOP call, `VOP_VPUT_PAIR()` or explicit releases, `vn_finished_write()`, and retry on `ERELOOKUP`.
- Capsicum rights are passed through `NDINIT_ATRIGHTS()` and descriptor helpers; open flags are converted to descriptor rights by `flags_to_rights()`.
- `O_PATH` is deliberately allowed only through selected paths, mainly `getvnode_path()`, while `getvnode()` rejects it for ordinary vnode file operations.
- MAC and AUDIT hooks are interleaved at syscall boundaries and before sensitive VOPs.
- Jail/prison visibility is enforced for statfs-style reporting with `prison_canseemount()` and `prison_enforce_statfs()`.

Research relevance:
- This file is the best map of FreeBSD's syscall-to-VFS boundary.
- It shows how FreeBSD combines path lookup policy, capability rights, vnode locking, mount write suspension, ABI compatibility, and filesystem-specific VOP dispatch.
- For filesystem implementation work, the expected VOP contracts for create/link/remove/rename/stat/readdir/readlink/fsync/copy-range are visible here through their callers.
