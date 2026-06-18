# File Research: sources/os/bsd/openbsd-src/sys/sys/syscall.h

Generated system call number table.

This generated header maps OpenBSD system call names to numeric `SYS_*` identifiers and records return/argument comments from `syscalls.master`. It spans process, file, VFS, VM, signal, socket, SysV IPC, kqueue, pledge/unveil, routing-table, thread, and `*at` interfaces, with obsolete slots preserved as comments to maintain ABI numbering. `SYS_MAXSYSCALL` is 331.

Filesystem-facing entries include open/close/read/write, link/unlink/rename, stat/lstat/fstat/fstatat, chmod/chown/chflags, mkdir/rmdir/mknod/mkfifo, mount/unmount/sync/fsync, statfs/getfsstat/fhstatfs, getfh/fhopen/fhstat, pathconf, truncate/ftruncate, pread/pwrite variants, quotactl, access/faccessat, openat, readlinkat, renameat, symlinkat, unlinkat, and `__getcwd`.

Filesystem/storage relevance: central syscall ABI map for every user-to-kernel filesystem entry point. The file is generated and should not be manually edited.
