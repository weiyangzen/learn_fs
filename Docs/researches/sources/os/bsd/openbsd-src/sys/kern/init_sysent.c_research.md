# File Research: sources/os/bsd/openbsd-src/sys/kern/init_sysent.c

Generated OpenBSD syscall switch table.

Key behavior:
- Declares `const struct sysent sysent[]`.
- Generated from `syscalls.master`; explicitly marked do-not-edit.
- Each entry records argument count, argument struct size, flags such as `SY_NOLOCK`, and handler function.
- Includes conditional syscall entries for `PTRACE`, `ACCOUNTING`, NFS, SysV IPC, and other compile-time options.
- Filesystem-heavy entries include `open`, `close`, `link`, `unlink`, `chdir`, `fchdir`, `mknod`, `chmod`, `chown`, `mount`, `unmount`, `stat`, `lstat`, `fstatat`, `sync`, `revoke`, `symlink`, `readlink`, `execve`, `chroot`, `getfsstat`, `statfs`, `fstatfs`, `fhstatfs`, `fsync`, `getdents`, `rename`, `flock`, `mkfifo`, `quotactl`, `getfh`, `truncate`, `ftruncate`, `pathconf*`, `fhopen`, `fhstat`, `__getcwd`, and the `*at` family.

Filesystem/OS relevance:
- Kernel dispatch table tying user ABI numbers to filesystem, VM, process, and device syscalls.
