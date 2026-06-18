# File Research: sources/os/bsd/netbsd-src/sys/sys/unistd.h

Read completely: 347 lines.

Defines POSIX feature constants and system/path configuration identifiers.

Key elements:
- Defines compile-time POSIX and POSIX.2 versions, job control, spawn support, and many POSIX option macros.
- Defines access mode constants `F_OK`, `X_OK`, `W_OK`, and `R_OK`.
- Defines `SEEK_SET`, `SEEK_CUR`, `SEEK_END`, and NetBSD legacy aliases.
- NetBSD mode defines `fsync_range` flags `FDATASYNC`, `FFILESYNC`, and `FDISKSYNC`.
- Defines `_PC_*` pathconf names including ACL and sparse-file hole extensions.
- Defines `_SC_*` sysconf names for POSIX, X/Open, threading, AIO, message queues, semaphores, CPU pages, processor counts, and scheduler ranges.
- Defines `_CS_PATH`.

Risks and notes:
- Numeric `pathconf`/`sysconf` identifiers are ABI with libc/kernel expectations.
- Comments require sysconf support when option macros are set to zero.
