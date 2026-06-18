# File Research: sources/os/bsd/netbsd-src/sys/sys/fcntl.h

Read completely: 366 lines.

## Purpose
Defines open/fcntl file status flags, descriptor flags, advisory lock structures, file seals, filesystem-control fcntl encoding, seek constants, fadvise constants, `*at` flags, and userland declarations.

## Main Interfaces
- Open flags: `O_RDONLY`, `O_WRONLY`, `O_RDWR`, `O_NONBLOCK`, `O_APPEND`, `O_SYNC`, `O_NOFOLLOW`, `O_CREAT`, `O_TRUNC`, `O_EXCL`, `O_NOCTTY`, `O_DSYNC`, `O_RSYNC`, `O_DIRECT`, `O_DIRECTORY`, `O_CLOEXEC`, `O_SEARCH`, `O_NOSIGPIPE`, `O_REGULAR`, `O_EXEC`, `O_CLOFORK`.
- Kernel conversions: `FFLAGS`, `OFLAGS`, `O_MASK`, `FMASK`, `FCNTLFLAGS`.
- Fcntl commands: `F_DUPFD`, `F_GETFD`, `F_SETFD`, `F_GETFL`, `F_SETFL`, locks, `F_CLOSEM`, `F_MAXFD`, `F_DUPFD_CLOEXEC`, `F_GETPATH`, file seals, `F_DUPFD_CLOFORK`, `F_DUPFD_CLOBOTH`.
- Descriptor flags: `FD_CLOEXEC`, `FD_CLOFORK`.
- Locking: `struct flock`, `F_RDLCK`, `F_UNLCK`, `F_WRLCK`, `LOCK_SH`, `LOCK_EX`, `LOCK_NB`, `LOCK_UN`.
- Seals: `F_SEAL_*`.
- Filesystem fcntl encoding: `F_FSCTL`, `F_FSIN`, `F_FSOUT`, `_FCN*`, `_FCN_FSPRIV*`.
- `POSIX_FADV_*`; `AT_FDCWD`, `AT_EACCESS`, symlink and remove-directory flags.
- Userland: `open`, `creat`, `fcntl`, `flock`, `posix_fadvise`, `posix_fallocate`, `openat`.

## Dependencies And Integration
Feeds VFS open, file descriptor state, vnode fileops, advisory locks, filesystem private fcntls, posix fallocate/fadvise, and `*at` syscalls.

## Risks And Edge Cases
- Open flags and kernel `f_flag` differ by `+1` conversion.
- Feature-test macros gate visibility of POSIX/XSI/NetBSD extensions.
- `O_CLOFORK` and `FD_CLOFORK` are newer ABI additions.
- Filesystem-control fcntl encodes parameter length and private filesystem number.

## Filesystem Relevance
High. This is the main open/fcntl ABI for filesystems and file descriptors.
