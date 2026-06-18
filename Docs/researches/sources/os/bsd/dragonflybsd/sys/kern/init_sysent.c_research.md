# File Research: sources/os/bsd/dragonflybsd/sys/kern/init_sysent.c

## Summary
Generated system call dispatch table. It maps syscall numbers to argument sizes, message sizes, and kernel syscall handler functions.

## Main Responsibilities
- Defines `struct sysent sysent[]`.
- Uses `AS(name)` to express argument structure size in register units.
- Maps active, obsolete, compatibility, module-reserved, and unimplemented syscall slots.
- Covers syscalls 0 through 555 in this snapshot.

## Filesystem-Relevant Entries
Includes core filesystem and VFS operations such as `open`, `close`, `link`, `unlink`, `chdir`, `fchdir`, `mknod`, `chmod`, `chown`, `mount`, `unmount`, `sync`, `revoke`, `symlink`, `readlink`, `execve`, `umask`, `chroot`, `msync`, `munmap`, `mprotect`, `madvise`, `rename`, `flock`, `mkdir`, `rmdir`, `utimes`, `quotactl`, `getfh`, `statfs`, `fstatfs`, `fhstatfs`, `fhopen`, ACL syscalls, extattr syscalls, `sendfile`, modern `*at` calls, `statvfs`, `fstatvfs`, `fhstatvfs`, `getvfsstat`, `fexecve`, `posix_fallocate`, `fdatasync`, and `futimesat`.

## Important Behavior
Many historical or reserved slots dispatch to `sys_nosys`; slots 210-219 dispatch to `sys_lkmnosys` for loadable module syscall placeholders. The file is marked do-not-edit and regenerated from `syscalls.master`.

## Risks
Manual edits will be overwritten. Dispatch table, syscall numbers, generated prototypes, syscall headers, and user ABI must remain synchronized.
