# File Research: sources/os/bsd/dragonflybsd/sys/kern/syscalls.c

## Summary
Generated syscall-name table for DragonFly BSD. It maps syscall numbers 0 through 555 to string names used for tracing, diagnostics, and ABI introspection.

## Main Responsibilities
- Defines `const char *syscallnames[]`.
- Names active syscalls, obsolete syscalls, compatibility entries, reserved holes, `nosys` slots, and loadable syscall placeholders.
- Documents the generation path: edit `syscalls.master`, then run `make sysent`.

## Important Contents
The table covers core process, VFS, descriptor, socket, memory-management, SysV IPC, POSIX message queue, kqueue, module, jail, varsym, VM-space, LWP, `*at`, and newer filesystem-adjacent syscalls. Filesystem-relevant names include `open`, `close`, `link`, `unlink`, `chdir`, `mknod`, `chmod`, `mount`, `unmount`, `sync`, `revoke`, `symlink`, `readlink`, `execve`, `chroot`, `msync`, `rename`, `flock`, `mkfifo`, `mkdir`, `rmdir`, `utimes`, `quotactl`, `statfs`, `fstatfs`, `getfh`, `fhstatfs`, `fhopen`, ACL and extattr calls, `sendfile`, `statvfs`, `getvfsstat`, `openat`, `fstatat`, `unlinkat`, `renameat`, `mkdirat`, `mknodat`, `readlinkat`, `symlinkat`, `linkat`, `fexecve`, `posix_fallocate`, `fdatasync`, and `futimesat`.

## Dependencies and Integration
This file must stay synchronized with `syscalls.master`, generated syscall prototypes, syscall numbers, and the dispatch table in `init_sysent.c`.

## Risks
Manual edits will be overwritten. Any mismatch between this name table and the actual syscall dispatch ABI can mislead tracing, debugging, and compatibility tooling.
