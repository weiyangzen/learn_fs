# sources/user-network-fs/nfs-ganesha/src/include/os/freebsd/syscalls.h

## Purpose
This FreeBSD portability header supplies missing Linux-style `*at` and file-handle syscall declarations used by NFS-Ganesha's VFS/FSAL layers. It lets common code compile against older FreeBSD environments that may not expose `openat`, `fstatat`, `getfhat`, file-handle link/readlink helpers, or `AT_*` constants.

## Important APIs, Types, And Control Flow
The file defines fallback `AT_FDCWD`, `AT_SYMLINK_NOFOLLOW`, `AT_SYMLINK_FOLLOW`, and `AT_REMOVEDIR` values, then conditionally declares `getfhat`, `fhlink`, and `fhreadlink` for newer FreeBSD compiler versions. If `SYS_openat` is absent it declares `openat`, `fchownat`, `futimesat`, `fstatat`, `getfhat`, `fhopenat`, `fchmodat`, `faccessat`, `linkat`, `mkdirat`, `mkfifoat`, `mknodat`, `unlinkat`, `readlinkat`, `symlinkat`, `renameat`, `utimensat`, and file-handle helpers.

## State And Persistence
There is no runtime state. The persistent behavior is compile-time ABI exposure: consumers either use system declarations or these prototypes to call platform implementations elsewhere.

## Dependencies And Integration Points
It depends on FreeBSD `<sys/mount.h>` and `<sys/syscall.h>` for `fhandle_t`, syscall numbers, and mount types. It integrates with platform-specific VFS code that needs file-handle-based lookup and relative-directory operations for NFS exports.

## Risks And Test Signals
Prototype drift against newer FreeBSD libc/kernel headers is the main risk, especially `char *` versus `const char *` signatures and `struct fhandle` spelling. Compile tests on supported FreeBSD versions should verify no duplicate/conflicting prototypes, while runtime tests should exercise filehandle open/link/readlink, symlink no-follow behavior, and all `*at` fallbacks.
