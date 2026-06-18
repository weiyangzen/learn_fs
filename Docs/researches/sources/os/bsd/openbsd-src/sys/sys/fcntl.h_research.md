# File Research: sources/os/bsd/openbsd-src/sys/sys/fcntl.h

This header defines open/fcntl flags, file descriptor flags, file locking ABI, and related libc prototypes.

Key definitions:
- Open modes/status flags: `O_RDONLY`, `O_WRONLY`, `O_RDWR`, `O_ACCMODE`, `O_NONBLOCK`, `O_APPEND`, `O_SYNC`, `O_DSYNC`, `O_RSYNC`, `O_NOFOLLOW`, `O_CREAT`, `O_TRUNC`, `O_EXCL`, `O_NOCTTY`, `O_CLOEXEC`, `O_DIRECTORY`, `O_CLOFORK`.
- BSD-visible kernel/compat aliases: `FREAD`, `FWRITE`, `FAPPEND`, `FASYNC`, `FFSYNC`, `FNONBLOCK`, `FNDELAY`, `O_NDELAY`.
- Kernel conversions: `FFLAGS`, `OFLAGS`, `FMASK`, `FCNTLFLAGS`.
- `fcntl` commands including POSIX.1-2024 `F_DUPFD_CLOFORK`.
- Descriptor flags: `FD_CLOEXEC`, `FD_CLOFORK`.
- Locking: `struct flock`, `F_RDLCK`, `F_UNLCK`, `F_WRLCK`, kernel lock flags, BSD `LOCK_*`.
- `*at` constants: `AT_FDCWD`, `AT_EACCESS`, `AT_SYMLINK_NOFOLLOW`, `AT_SYMLINK_FOLLOW`, `AT_REMOVEDIR`.

Userland declarations:
- `open`, `creat`, `fcntl`, `flock`, `openat`.

Risk notes:
- `FFLAGS`/`OFLAGS` rely on OpenBSD’s read/write bit encoding being one greater than open access mode.
- POSIX visibility controls whether newer close-on-fork interfaces are exposed.
