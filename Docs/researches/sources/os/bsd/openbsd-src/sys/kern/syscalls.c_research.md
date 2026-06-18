# File Research: sources/os/bsd/openbsd-src/sys/kern/syscalls.c

Generated system-call name table for OpenBSD.

Contents:
- Defines `const char *const syscallnames[]`.
- Maps syscall numbers 0 through 330 to printable names or placeholder strings for obsolete/unimplemented entries.
- Includes conditional names based on kernel options such as `PTRACE`, `KTRACE`, `ACCOUNTING`, `NFSCLIENT`, `NFSSERVER`, `SYSVSEM`, `SYSVMSG`, and `SYSVSHM`.

Role:
- Provides stable syscall-number-to-name metadata for tracing, diagnostics, ktrace-like output, and kernel/user debugging.
- The header warns that it is generated from `syscalls.master`, not edited manually.

Filesystem/storage relevance:
- Contains no implementation logic. It identifies filesystem-related syscall names such as `open`, `close`, `link`, `unlink`, `mount`, `unmount`, `stat`, `fstat`, `getfsstat`, `statfs`, `fstatfs`, `fsync`, `getdents`, `rename`, `mkdir`, `rmdir`, `quotactl`, pathconf variants, `fhopen`, `fhstat`, and many `*at` calls.
