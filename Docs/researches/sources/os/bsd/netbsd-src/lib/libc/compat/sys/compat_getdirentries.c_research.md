# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_getdirentries.c

Read completely: 51 lines.

This implements compatibility-only `getdirentries`. It stores the current directory offset from `lseek(fd, 0, SEEK_CUR)` into `*basep`, then calls the compatibility `getdents`.

Security/reliability notes: dereferences `basep` unconditionally. The warning notes this interface is compatibility-only and callers should prefer `getdents` or `readdir`.
