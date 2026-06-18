# File Research: sources/os/bsd/openbsd-src/sys/sys/syscallargs.h

Generated syscall argument structs and handler prototypes.

This generated header defines the `syscallarg(x)` union used to extract syscall arguments correctly on little- and big-endian machines, then declares one argument struct per syscall that takes arguments. The structs cover file/VFS, VM, sockets, signals, process control, SysV IPC, kqueue, threads, pledge/unveil, and `*at` variants.

The second half declares kernel handler prototypes for implemented syscalls, with compile-time feature gates for optional subsystems such as `PTRACE`, `KTRACE`, `ACCOUNTING`, NFS, and SysV IPC. Filesystem-facing prototypes include open, mount, stat families, file-handle calls, sync/fsync, getdents, access, chmod/chown/chflags, link/unlink/rename/symlink/readlink, directory creation/removal, fifo/node creation, truncate, positioned I/O, pathconf, quotactl, and `openat`/`unlinkat`/related calls.

Filesystem/storage relevance: central kernel ABI glue for filesystem syscalls. Like `syscall.h`, it is generated from `syscalls.master` and should be changed by editing the generator input, not this file.
