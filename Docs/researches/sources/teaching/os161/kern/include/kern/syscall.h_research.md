# File Research: sources/teaching/os161/kern/include/kern/syscall.h

Defines OS/161 syscall numbers.

Key groups:
- Process, VM, credentials, signals, file handles, pathnames, current directory, symlinks, mount, stat/timestamps/permissions, sockets, time, sync/reboot.
- Marked `CALLBEGIN`/`CALLEND` for script generation of syscall stubs.

Filesystem-relevant calls:
- `open`, `read`, `write`, `getdirentry`, `lseek`, `ftruncate`, `fsync`, `ioctl`.
- `link`, `remove`, `mkdir`, `rmdir`, `rename`, `chdir`, `getcwd`, `mount`, `unmount`.
- `stat`, `fstat`, `lstat`, `sync`.

Relevance:
- VFS dispatch ultimately maps many of these syscalls to SFS/semfs vnode/fs operations.
